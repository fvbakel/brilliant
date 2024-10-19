import graphviz
from genetic_nn.creature_basics import (
    Creature, 
    Neuron,NeuronType,
    Sensor,Action,
    ALL_SENSOR_TYPES,
    ALL_ACTION_TYPES,
    NR_OF_HIDDEN_NEURONS
)

class Gen2Graphviz:

    def __init__(self,creature:Creature):
        self.creature:Creature = creature
        self.use_full_only     = False
        self.reset()        
 
    def reset(self):
        self._sub_graphs: dict[str, graphviz.Digraph] = dict()
        self.dot = graphviz.Digraph()

    def makePlainGraph(self):
        self.dot.attr(rankdir='LR')
        neuron_ids:set[int] = set()
        for gen in self.creature.gens:
            neuron_ids.add(gen.from_neuron.id)
            neuron_ids.add(gen.to_neuron.id)
        for id in neuron_ids:
            self.dot.node(name=str(id))
            self.dot.node(name=str(id))
        
        self._addChildRelations()

    def makeSimpleClusterGraph(self):
        self.dot.attr(rankdir='LR')
        self._addSimpleClusters()
        self._addChildRelations()
    
    def _addNodeForNeuron(self,graph:graphviz.Digraph,neuron:Neuron):
        if neuron in self.creature.use_full_neurons:
            color='black'
        else:
            color='lightgrey'
        graph.node(name=str(neuron.id),label=f'{neuron.type.value} {neuron.type_index}',color=color,fontcolor=color)

    
    def _addNodeForSensor(self,graph:graphviz.Digraph,index:int,sensor:Sensor):
        graph.node(name=f'sensor_{index}',label=f'sensor_{index} {sensor.type.name}')
    
    def _addNodeForAction(self,graph:graphviz.Digraph,index:int,action:Action):
        graph.node(name=f'action_{index}',label=f'action_{index} {action.type.name}')

    def _makeSubGraph(self,name:str):
        self._sub_graphs[name] = graphviz.Digraph(name=name)
        self._sub_graphs[name].attr(rankdir='TD',color='lightgrey',label=name)

    def _addSimpleClusters(self):
        
        self._makeSubGraph(name=f'cluster_sensors')
        for type in NeuronType.list():
            self._makeSubGraph(name=f'cluster_{type}')
        self._makeSubGraph(name=f'cluster_actions')

        for index,sensor in enumerate(self.creature.sensors):
            self._addNodeForSensor(self._sub_graphs[f'cluster_sensors'],index,sensor)
        
        """
        # force order with a hidden edge
        # does not work :-(
        for index,sensor in enumerate(self.creature.sensors[:-1]):
            from_node_id = f'sensor_{index}'
            to_node_id = f'sensor_{index +1 }'
            self._sub_graphs[f'cluster_sensors'].edge(from_node_id,to_node_id) #,style='invis')
        """

        neurons:dict[int,Neuron] = dict()
        for gen in self.creature.gens:
            neurons[gen.from_neuron.id] = gen.from_neuron
            neurons[gen.to_neuron.id] = gen.to_neuron
        for id,neuron in neurons.items():
            self._addNodeForNeuron(self._sub_graphs[f'cluster_{neuron.type.value}'],neuron)
        

        for index,action in enumerate(self.creature.actions):
            self._addNodeForAction(self._sub_graphs[f'cluster_actions'],index,action)

        for name,graph in self._sub_graphs.items():
            self.dot.subgraph(graph)

    def _addChildRelations(self):
        for index,sensor in enumerate(self.creature.sensors):
            from_node_id = f'sensor_{index}'
            #to_node_id = f'{NeuronType.INPUT.value} {ALL_SENSOR_TYPES.index(sensor.type)}'
            to_node_id = f'{ALL_SENSOR_TYPES.index(sensor.type)}'
            self.dot.edge(from_node_id,to_node_id)

        for gen in self.creature.gens:
            if gen.use_full:
                color = 'black'
            else:
                color = 'lightgrey'
            self.dot.edge(str(gen.from_neuron.id),str(gen.to_neuron.id),label=f'{gen.weight}',color=color,fontcolor=color)

        for index,action in enumerate(self.creature.actions):
            from_node_id = f'{ALL_ACTION_TYPES.index(action.type) + NR_OF_HIDDEN_NEURONS + len(ALL_SENSOR_TYPES)}'
            to_node_id = f'action_{index}'
            self.dot.edge(from_node_id,to_node_id)

    def render(self,filename:str,directory:str, format='svg'):
        self.dot.render(filename=filename,directory=directory, format=format)

    