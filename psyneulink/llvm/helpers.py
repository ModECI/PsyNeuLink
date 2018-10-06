# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


# ********************************************* PNL LLVM helpers **************************************************************

from llvmlite import ir


def for_loop(builder, start, stop, inc, body_func, id):
    # Initialize index variable
    assert(start.type is stop.type)
    index_var = builder.alloca(stop.type)
    builder.store(start, index_var)

    # basic blocks
    cond_block = builder.append_basic_block(id + "-cond")
    out_block = None

    # Loop condition
    builder.branch(cond_block)
    with builder.goto_block(cond_block):
        tmp = builder.load(index_var)
        cond = builder.icmp_signed("<", tmp, stop)

        # Loop body
        with builder.if_then(cond, likely=True):
            index = builder.load(index_var)
            if (body_func is not None):
                body_func(builder, index)
            index = builder.add(index, inc)
            builder.store(index, index_var)
            builder.branch(cond_block)

        out_block = builder.block

    return ir.IRBuilder(out_block)


def for_loop_zero_inc(builder, stop, body_func, id):
    start = stop.type(0)
    inc = stop.type(1)
    return for_loop(builder, start, stop, inc, body_func, id)


def fclamp(builder, val, min_val, max_val):
    cond = builder.fcmp_unordered("<", val, min_val)
    tmp = builder.select(cond, min_val, val)
    cond = builder.fcmp_unordered(">", tmp, max_val)
    return builder.select(cond, max_val, tmp)


def fclamp_const(builder, val, min_val, max_val):
    minval = val.type(min_val)
    maxval = val.type(max_val)
    return fclamp(builder, val, minval, maxval)

def load_extract_scalar_array_one(builder, ptr):
    val = builder.load(ptr)
    if isinstance(val.type, ir.ArrayType) and val.type.count == 1:
        val = builder.extract_value(val, [0])
    return val

def __ts_compare(ctx, builder, ts1, ts2, comp):
    assert comp == '<'
    part_eq = []
    part_cmp = []

    for element in range(3):
        a = builder.extract_value(ts1, element)
        b = builder.extract_value(ts2, element)
        part_eq.append(builder.icmp_unsigned('==', a, b))
        part_cmp.append(builder.icmp_unsigned(comp, a, b))

    trial = builder.and_(builder.not_(part_eq[0]), part_cmp[0])
    run = builder.and_(part_eq[0],
                       builder.and_(builder.not_(part_eq[1]), part_cmp[1]))
    step = builder.and_(builder.and_(part_eq[0], part_eq[1]),
                        part_cmp[2])

    return step
    return builder.or_(trial, builder.or_(run, step))

def generate_sched_condition(ctx, builder, condition, cond_ptr, comp_nodes, node):

    from psyneulink.scheduling.condition import All, AllHaveRun, Always, EveryNCalls
    if isinstance(condition, Always):
        return ir.IntType(1)(1)
    elif isinstance(condition, All):
        agg_cond = ir.IntType(1)(1)
        for cond in condition.args:
            cond_res = generate_sched_condition(ctx, builder, cond, cond_ptr, comp_nodes, node)
            agg_cond = builder.and_(agg_cond, cond_res)
        return agg_cond
    elif isinstance(condition, AllHaveRun):
        run_cond = ir.IntType(1)(1)
        array_ptr = builder.gep(cond_ptr, [ctx.int32_ty(0), ctx.int32_ty(1)])
        for idx, _ in enumerate(comp_nodes):
            node_runs_ptr = builder.gep(array_ptr, [ctx.int32_ty(0),
                                        ctx.int32_ty(idx), ctx.int32_ty(0)])
            node_runs = builder.load(node_runs_ptr)
            node_ran = builder.icmp_unsigned('>', node_runs, ctx.int32_ty(0))
            return builder.and_(run_cond, node_ran)
    elif isinstance(condition, EveryNCalls):
        target, count = condition.args

        zero = ctx.int32_ty(0)
        target_idx = ctx.int32_ty(comp_nodes.index(target))

        array_ptr = builder.gep(cond_ptr, [zero, ctx.int32_ty(1)])
        target_status = builder.load(builder.gep(array_ptr, [zero, target_idx]))

        # Check number of runs
        target_runs = builder.extract_value(target_status, 0, target.name + " runs")
        ran = builder.icmp_unsigned('>', target_runs, zero)
        remainder = builder.urem(target_runs, ctx.int32_ty(count))
        divisible = builder.icmp_unsigned('==', remainder, zero)
        completedNruns = builder.and_(ran, divisible)

        # Check that we have not run yet
        my_idx = ctx.int32_ty(comp_nodes.index(node))
        my_time_stamp_ptr = builder.gep(array_ptr, [zero, my_idx, ctx.int32_ty(1)])
        my_time_stamp = builder.load(my_time_stamp_ptr)
        target_time_stamp = builder.extract_value(target_status, 1)
        ran_after_me = __ts_compare(ctx, builder, my_time_stamp, target_time_stamp, '<')

        # Return: target.calls % N == 0 AND me.last_time < target.last_time
        return builder.and_(completedNruns, ran_after_me)
    else:
        print("ERROR: Unsupported scheduling condition: ", condition)
        assert False
