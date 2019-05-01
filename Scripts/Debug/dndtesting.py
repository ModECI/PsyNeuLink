# -*- coding: utf-8 -*-
"""DNDtesting.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XjXuOsceGgDSyGsSF8OVQvQS4h-L-U4F
"""

# !pip install --upgrade psyneulink

import psyneulink as pnl
import numpy as np
print(pnl.__version__)

# network params
n_input = 2
n_hidden = 5
n_output = 1
max_entries = 7

# training params
num_epochs = 3
learning_rate = .1
wts_init_scale = .1

# layers

input = pnl.TransferMechanism(
    name='input',
    default_variable=np.zeros(n_input)
)

hidden = pnl.TransferMechanism(
    name='hidden',
    default_variable=np.zeros(n_hidden),
    function=pnl.Logistic()
)

output = pnl.TransferMechanism(
    name='output',
    default_variable=np.zeros(n_output),
    function=pnl.Logistic()
)

# weights
w_ih = pnl.MappingProjection(
    name='input_to_hidden',
    matrix=np.random.randn(n_input, n_hidden)*wts_init_scale,
    sender=input,
    receiver=hidden
)

w_ho = pnl.MappingProjection(
    name='hidden_to_output',
    matrix=np.random.randn(n_hidden, n_output)*wts_init_scale,
    sender=hidden,
    receiver=output
)

# dnd
dnd = pnl.EpisodicMemoryMechanism(
    cue_size=n_hidden, assoc_size=n_hidden,
    name='dnd'
)

w_hdc = pnl.MappingProjection(
    name='hidden_to_cue',
    matrix=np.random.randn(n_hidden, n_hidden)*wts_init_scale,
    sender=hidden,
    receiver=dnd.input_states[pnl.CUE_INPUT]
)

w_hda = pnl.MappingProjection(
    name='hidden_to_assoc',
    matrix=np.random.randn(n_hidden, n_hidden)*wts_init_scale,
    sender=hidden,
    receiver=dnd.input_states[pnl.ASSOC_INPUT]
)


w_dh = pnl.MappingProjection(
    name='em_to_hidden',
    matrix=np.random.randn(n_hidden, n_hidden)*wts_init_scale,
    sender=dnd,
    receiver=hidden
)

comp = pnl.Composition(name='xor')

# add all nodes
all_nodes = [input, hidden, output, dnd]
for node in all_nodes:
    comp.add_node(node)
# input-hidden-output pathway
comp.add_projection(sender=input, projection=w_ih, receiver=hidden)
comp.add_projection(sender=hidden, projection=w_ho, receiver=output)
# conneciton, dnd
comp.add_projection(sender=dnd, projection=w_dh, receiver=hidden)
comp.add_projection(
    sender=hidden,
    projection=w_hdc,
    receiver=dnd.input_states[pnl.CUE_INPUT]
)
comp.add_projection(
    sender=hidden,
    projection=w_hda,
    receiver=dnd.input_states[pnl.ASSOC_INPUT]
)
# show graph
comp.show_graph(output_fmt='jupyter')

# # comp.show()
# # the required inputs for dnd
# print('dnd input_states: ', dnd.input_states.names)
#
# # currently, dnd receive info from the following node
# print('dnd receive: ')
# for dnd_input in dnd.input_states.names:
#     afferents = dnd.input_states[dnd_input].path_afferents
#     if len(afferents) == 0:
#         print(f'- {dnd_input}: NA')
#     else:
#         sending_node_name = afferents[0].sender.owner.name
#         print(f'- {dnd_input}: {sending_node_name}')
#
# print('dnd cue input: ', dnd.input_states.names)
#
# print('hidden receive: ')
# for hidden_afferent in hidden.input_states[0].path_afferents:
#     print('- ', hidden_afferent.sender.owner.name)

# comp.show()
 # the required inputs for dnd
print('dnd input_states: ', dnd.input_states.names)
  
# currently, dnd receive info from the following node
print('dnd receive: ')
for dnd_input in dnd.input_states.names:
    afferents = dnd.input_states[dnd_input].path_afferents
    if len(afferents) == 0:
        print(f'- {dnd_input}: NA')
    else:
        sending_node_name = afferents[0].sender.owner.name
        print(f'- {dnd_input}: {sending_node_name}')

print('dnd cue input: ', dnd.input_states.names)

print('hidden receive: ')
for hidden_afferent in hidden.input_states[0].path_afferents:
    print('- ', hidden_afferent.sender.owner.name)

print(dnd.output_states.names)
print(dnd.output_states.values)

print(input)


#comp.run([1,1])
#print(dnd.values)
#dnd.dict.insert_memory([1,1])

print(dnd.output_states.values)

input = [0,1]
print(dnd.input_states)
print(hidden.value)
print(output.value)


#comp.run(input)

print(comp.run([1,1]))
print(comp.run([2,2]))

print(comp.run([100,100]))

print(comp.run([10000,100000]))

#comp.output.value

input_dict = [[0,1], [1,2], [2,3], [3,4], [4,5]]
result = comp.run(inputs=input_dict, execution_id = 5) #, do_logging=True)
print(dnd.input_values)
print(hidden.value)

print(dnd.output_values)

result1 = comp.run([0,1])
result2 = comp.run([0,2])

print(result1)
print(result2)

print(output.output_values)

dnd.CUE_INPUT = [1,1,1,1,1]
dnd.ASSOC_INPUT = [1,2,3,4,5]

print(dnd.input_values)
print(dnd.output_values)

# dnd.function.insert_memories([[[100,101,102,103,104],[23,24,25,26,27]]], execution_id=5)
# assert True

# dnd.dict.insert_memory({0,1})
#
# dnd.get_memory(0)

"""cant figure out get&store memory functions"""
