import random, math, pygame, numpy
CONST_mutationRate = .2
CONST_numMutations = 90
#random.seed(1)

def sigmoid(x):
    return 1 / (1+math.exp(-x))

# A hidden node object consisting of weights and an activation function
# as well as the ability to mutate a random weight
class NetNode:
    # Array of floats
    weights = []
    total = 0
    
    # Defines a node with given weights
    def __init__(self, weights):
        self.weights = weights
    
    # Returns true if is output layer
    def isOutput(self):
        if len(self.weights) == 0:
            return True
        return False
    
    # Randomly picks weights between other node and this node, returns weights
    def Breed(self, other):
        weights = self.weights.copy()
        for i in range(len(weights)):
            if numpy.random.uniform(0.0,1.0) > 0.5:
                weights[i] = other.weights[i]
        return weights
    
    # Activation function for node. Returns some number based on inputs.
    def AF(self, inputs):
        addition = 0
        for i in range(len(inputs)):
            addition += inputs[i]
        addition = sigmoid(addition)
        self.total = addition
        return addition
    
    # Randomly chooses a weight and randomly adjusts it.
    def Mutate(self):
        # Positive or negative mutation
        m = numpy.random.uniform(-1, 1)
        wC = int(numpy.random.uniform(0,len(self.weights)))
        if m == 0:
            m = 1
        self.weights[wC] += m * CONST_mutationRate

# A layer of NetNodes
class NetLayer:
    # Array of NetNodes
    nodes = None
    # Takes in 2 dimensional array of weights
    def __init__(self, tweights):
        self.nodes = []
        for i in range(len(tweights)):
            self.nodes.append(NetNode(tweights[i]))
    
    # Breeds with another net layer
    def Breed(self, other):
        tweights = []
        for i in range(len(self.nodes)):
            tweights.append(self.nodes[i].Breed(other.nodes[i]))
        return tweights
    
    # Mutates a random node
    def Mutate(self):
        n = int(numpy.random.uniform(0,len(self.nodes)))
        self.nodes[n].Mutate()
    
    # Sets all of nodes to appropriate total
    def calculateAllNodes(self, previousLayer):
        for i in range(len(self.nodes)):
            self.calculateNode(previousLayer, i)
    
    # Gets weights and totals of all nodes for this node and appends to input, then adds to node
    def calculateNode(self, previousLayer, nodeNum):
        inputs = []
        for i in range(len(previousLayer.nodes)):
            w = previousLayer.nodes[i].weights[nodeNum]
            a = previousLayer.nodes[i].total
            inputs.append(w * a)
        self.nodes[nodeNum].AF(inputs)
    
    # Returns true if is output layer
    def isOutputLayer(self):
        return self.nodes[0].isOutput()
    
    # Sets layer node weights
    def setNodeWeights(self, nodeNum, weights):
        self.nodes[nodeNum].weights = weights
    
    # Returns safe weights
    def getNodeWeights(self):
        arr = []
        for i in range(len(self.nodes)):
            lst = []
            for j in range(len(self.nodes[i].weights)):
                lst.append(self.nodes[i].weights[j])
            arr.append(lst)
        return arr

class NNetwork:
    layers = []
    outputs = []
    # Creates default nnetwork
    def __init__(self, numInputs, numHidden, numOutputs, numHiddenLayers):
        self.layers = []
        self.outputs = []
        inputsArr = self.InitializeLayer(numInputs, numHidden)
        #hiddenArr = self.InitializeLayer(numHidden, numOutputs)
        outputsArr = self.InitializeLayer(numOutputs, 0)
        inLayer = NetLayer(inputsArr)
        #hidLayer = NetLayer(hiddenArr)
        outLayer = NetLayer(outputsArr)
        
        for i in range(numHiddenLayers):
            hiddenArr = self.InitializeLayer
        
        self.layers.append(inLayer)
        for i in range(numHiddenLayers):
            nextLayerNum = 0
            if i == numHiddenLayers-1:
                nextLayerNum = numOutputs
            else:
                nextLayerNum = numHidden
                
            hiddenArr = self.InitializeLayer(numHidden, nextLayerNum)
            self.layers.append(NetLayer(hiddenArr))
        #self.layers.append(hidLayer)
        self.layers.append(outLayer)
    
    # Breeds with another NNetwork
    def Breed(self, other):
        for i in range(len(self.layers)):
            self.setWeights(i, self.layers[i].Breed(other.layers[i]))
    
    # Returns a deep copy of neural network
    def DeepCopy(self):
        nInputs = len(self.layers[0].nodes)
        nHidden = len(self.layers[1].nodes)
        nOut = len(self.layers[len(self.layers)-1].nodes)
        
        Network = NNetwork(nInputs, nHidden, nOut, len(self.layers)-2)
        for i in range(3):
            Network.setWeights(i, self.layers[i].getNodeWeights())
        return Network
        
    # Randomly mutates a layer
    def Mutate(self):
        for i in range(CONST_numMutations):
            n = int(numpy.random.uniform(0, len(self.layers)-1))
            self.layers[n].Mutate()
    
    # Calculates all of network based on inputs, stores outputs
    def calculateNetwork(self, inputs):
        for i in range(len(self.layers[0].nodes)):
            self.layers[0].nodes[i].total = inputs[i]
            
        for i in range(1, len(self.layers)):
            self.layers[i].calculateAllNodes(self.layers[i-1])
        
        length = len(self.layers)
        endLen = len(self.layers[length-1].nodes)
        self.outputs = []
        for i in range(endLen):
            self.outputs.append(self.layers[length-1].nodes[i].total)
        return self.outputs
        
    # Sets the weights of a given layer
    def setWeights(self, layerNum, tweights):
        layer = self.layers[layerNum]
        for i in range(len(layer.nodes)):
            layer.setNodeWeights(i, tweights[i])
        
    # Returns an arr of default weights of length
    def InitializeLayer(self, length, nextLen):
        arr = []
        for i in range(length):
            arrJ = []
            for j in range(nextLen):
                arrJ.append(0)#random.uniform(0,1)) #Default val
            arr.append(arrJ)
            
        return arr
    
    def print(self):
        for i in range(len(self.layers)):
            print("Layer " + str(i))
            for j in range(len(self.layers[i].nodes)):
                print(str(self.layers[i].nodes[j].total) + ", " +
                    str(self.layers[i].nodes[j].weights))
       





    
