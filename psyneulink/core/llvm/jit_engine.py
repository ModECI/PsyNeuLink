# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


# ********************************************* LLVM bindings **************************************************************

from llvmlite import binding

import os

from .builder_context import _find_llvm_function, _gen_cuda_kernel_wrapper_module

try:
    import pycuda
    from pycuda import autoinit as pycuda_default
    ptx_enabled = True
except:
    ptx_enabled = False


__all__ = ['cpu_jit_engine', 'ptx_enabled']

if ptx_enabled:
    __all__.append('ptx_jit_engine')


__dumpenv = os.environ.get("PNL_LLVM_DUMP")

# Compiler binding
__initialized = False
def _binding_initialize():
    global __initialized
    if not __initialized:
        binding.initialize()
        if not ptx_enabled:
            # native == currently running CPU. ASM printer includes opcode emission
            binding.initialize_native_target()
            binding.initialize_native_asmprinter()
        else:
            binding.initialize_all_targets()
            binding.initialize_all_asmprinters()

        __initialized = True


def _cpu_jit_constructor():
    _binding_initialize()

    # PassManagerBuilder can be shared
    __pass_manager_builder = binding.PassManagerBuilder()
    __pass_manager_builder.inlining_threshold = 99999  # Inline all function calls
    __pass_manager_builder.loop_vectorize = True
    __pass_manager_builder.slp_vectorize = True
    __pass_manager_builder.opt_level = 3  # Most aggressive optimizations

    __cpu_features = binding.get_host_cpu_features().flatten()
    __cpu_name = binding.get_host_cpu_name()

    # Create compilation target, use default triple
    __cpu_target = binding.Target.from_default_triple()
    __cpu_target_machine = __cpu_target.create_target_machine(cpu=__cpu_name, features=__cpu_features, opt=3)

    __cpu_pass_manager = binding.ModulePassManager()
    __cpu_target_machine.add_analysis_passes(__cpu_pass_manager)
    __pass_manager_builder.populate(__cpu_pass_manager)


    # And an execution engine with an empty backing module
    # TODO: why is empty backing mod necessary?
    # TODO: It looks like backing_mod is just another compiled module.
    #       Can we use it to avoid recompiling builtins?
    #       Would cross module calls work? and for GPUs?
    __backing_mod = binding.parse_assembly("")

    __cpu_jit_engine = binding.create_mcjit_compiler(__backing_mod, __cpu_target_machine)
    return __cpu_jit_engine, __cpu_pass_manager, __cpu_target_machine


def _ptx_jit_constructor():
    _binding_initialize()

    # PassManagerBuilder can be shared
    __pass_manager_builder = binding.PassManagerBuilder()
    __pass_manager_builder.inlining_threshold = 99999  # Inline all function calls
    __pass_manager_builder.loop_vectorize = True
    __pass_manager_builder.slp_vectorize = True
    __pass_manager_builder.opt_level = 3  # Most aggressive optimizations

    # Use default device
    # TODO: Add support for multiple devices
    __compute_capability = pycuda_default.device.compute_capability()
    __ptx_sm = "sm_{}{}".format(__compute_capability[0], __compute_capability[1])
    # Create compilation target, use 64bit triple
    __ptx_target = binding.Target.from_triple("nvptx64-nvidia-cuda")
    __ptx_target_machine = __ptx_target.create_target_machine(cpu=__ptx_sm, opt=3, codemodel='small')

    __ptx_pass_manager = binding.ModulePassManager()
    __ptx_target_machine.add_analysis_passes(__ptx_pass_manager)
#    __pass_manager_builder.populate(__ptx_pass_manager)

    return __ptx_pass_manager, __ptx_target_machine


def _try_parse_module(module):
    if __dumpenv is not None and __dumpenv.find("llvm") != -1:
        print(module)

    # IR module is not the same as binding module.
    # "assembly" in this case is LLVM IR assembly.
    # This is intentional design decision to ease
    # compatibility between LLVM versions.
    try:
        mod = binding.parse_assembly(str(module))
        mod.verify()
    except Exception as e:
        print("ERROR: llvm parsing failed: {}".format(e))
        mod = None

    return mod


class jit_engine:
    def __init__(self):
        self._jit_engine = None
        self._jit_pass_manager = None
        self._target_machine = None
        self.__mod = None
        self.__opt_modules = 0
        self.__dumpenv = str(os.environ.get("PNL_LLVM_DUMP"))

    def __del__(self):
        if self.__dumpenv.find("mod_count") != -1:
            print("Total JIT modules: ", self.__opt_modules)

    def opt_and_add_bin_module(self, module):
        self._pass_manager.run(module)
        if self.__dumpenv.find("opt") != -1:
            print(module)

        # This prints generated x86 assembly
        if self.__dumpenv.find("isa") != -1:
            print("ISA assembly:")
            print(self._target_machine.emit_assembly(module))

        self._engine.add_module(module)
        self._engine.finalize_object()
        self.__opt_modules += 1

    def _remove_bin_module(self, module):
        self._engine.remove_module(module)

    def opt_and_append_bin_module(self, module):
        if self.__mod is None:
            self.__mod = module
        else:
            self._remove_bin_module(self.__mod)
            # Linking here invalidates 'module'
            self.__mod.link_in(module)

        self.opt_and_add_bin_module(self.__mod)

    @property
    def _engine(self):
        if self._jit_engine is None:
            self._init()

        return self._jit_engine

    @property
    def _pass_manager(self):
        if self._jit_pass_manager is None:
            self._init()

        return self._jit_pass_manager

    # Unfortunately, this needs to be done for every jit_engine.
    # Liking step in opt_and_add_bin_module invalidates 'mod_bundle',
    # so it can't be linked mutliple times (in multiple engines).
    def compile_modules(self, modules, compiled_modules):
        # Parse generated modules and link them
        mod_bundle = binding.parse_assembly("")
        for m in modules:
            new_mod = _try_parse_module(m)
            if new_mod is not None:
                mod_bundle.link_in(new_mod)
                compiled_modules.add(m)

        self.opt_and_append_bin_module(mod_bundle)


class cpu_jit_engine(jit_engine):

    def __init__(self, object_cache = None):
        super().__init__()
        self._object_cache = object_cache

    def _init(self):
        assert self._jit_engine is None
        assert self._jit_pass_manager is None
        assert self._target_machine is None

        self._jit_engine, self._jit_pass_manager, self._target_machine = _cpu_jit_constructor()
        if self._object_cache is not None:
             self._jit_engine.set_object_cache(self._object_cache)

class ptx_jit_engine(jit_engine):
    class cuda_engine():
        def __init__(self, tm):
            self._modules = {}
            self._target_machine = tm

        def set_object_cache(cache):
            pass

        def add_module(self, module):
            try:
                ptx = self._target_machine.emit_assembly(module)
                ptx_mod = pycuda.driver.module_from_buffer(ptx.encode())
            except Exception as e:
                print("FAILED to generate PTX:", e)
                print(ptx)
                return None

            self._modules[module] = ptx_mod

        def finalize_object(self):
            pass

        def remove_module(self, module):
            self._modules.pop(module, None)

        def _find_kernel(self, name):
            function = None
            for m in self._modules.values():
                try:
                    function = m.get_function(name)
                except pycuda._driver.LogicError:
                    pass
            return function

    def __init__(self, object_cache = None):
        super().__init__()
        self._object_cache = object_cache

    def _init(self):
        assert self._jit_engine is None
        assert self._jit_pass_manager is None
        assert self._target_machine is None

        self._jit_pass_manager, self._target_machine = _ptx_jit_constructor()
        self._jit_engine = ptx_jit_engine.cuda_engine(self._target_machine)

    def get_kernel(self, name):
        kernel = self._engine._find_kernel(name + "_cuda_kernel")
        if kernel is None:
            function = _find_llvm_function(name);
            wrapper_mod = _gen_cuda_kernel_wrapper_module(function)
            self.compile_modules([wrapper_mod], set())
            kernel = self._engine._find_kernel(name + "_cuda_kernel")

        return kernel
