
#-----Imports-----#
import numpy as np

linear = lambda x: x
relu = lambda x: x * (x > 0)


def mutateArray(array, std, p):
    selected = np.random.random(array.shape) < p
    array[selected] += np.random.normal(0, std, np.sum(selected))

class Layer:

    def __init__(self, size, activation, nextLayer = None):

        self.size = size
        self.activation = activation
        self.nextLayer = nextLayer

        if nextLayer == None:
            pass
        else:
            self.M = np.random.normal(0, 0.1, size=(self.nextLayer.size, size))
            self.bias = np.random.normal(0, 0.1, size=nextLayer.size)


    def mutate(self, std, p):

        mutateArray(self.M, std, p)
        mutateArray(self.bias, std, p)

    def run(self, input):

        if self.nextLayer == None:
            return input

        output = self.nextLayer.activation(np.dot(self.M, input) + self.bias)

        return self.nextLayer.run(output)

    def copy(self, std, p):

        child = Layer(self.size, self.activation, self.nextLayer)

        if self.nextLayer != None:
            child.M = np.copy(self.M)
            child.bias = np.copy(self.bias)

            child.mutate(std, p)

        return child




class Network:

    def __init__(self, memorySize, memoryUpdateRate, mutateStd, mutateP, memoryHiddenSizes, decisionHiddenSizes):

        self.memorySize = memorySize
        self.memoryUpdateRate = memoryUpdateRate
        self.mutateStd, self.mutateP = mutateStd, mutateP
        self.memoryHiddenSizes = memoryHiddenSizes
        self.decisionHiddenSizes = decisionHiddenSizes

        self.memory = np.zeros(memorySize)

        self.memoryNetwork = self.setupMemoryNetwork()
        self.decisionNetwork = self.setupDecisionNetwork()

    #Network used for updating memory
    def setupMemoryNetwork(self):


        outLayer = Layer(self.memorySize, linear)

        memoryNetwork = [outLayer]

        for size in self.memoryHiddenSizes:
            h = Layer(size, relu, memoryNetwork[-1])
            memoryNetwork.append(h)

        inputLayer = Layer(4, relu, memoryNetwork[-1])
        memoryNetwork.append(inputLayer)

        return memoryNetwork

    def setupDecisionNetwork(self):

        outLayer = Layer(1, linear)

        decisionNetwork = [outLayer]

        for size in self.memoryHiddenSizes:
            h = Layer(size, relu, decisionNetwork[-1])
            decisionNetwork.append(h)

        inputLayer = Layer(self.memorySize + 3, relu, decisionNetwork[-1])
        decisionNetwork.append(inputLayer)

        return decisionNetwork


    def updateMemory(self, c: np.array, E: float):

        input = np.zeros(4)
        input[0:3] = c
        input[3] = E

        newMemory = self.memoryNetwork[-1].run(input)
        self.memory = self.memoryUpdateRate * newMemory + (1 - self.memoryUpdateRate) * self.memory


    def decide(self, c: np.array):

        input = np.zeros(self.memorySize + 3)
        input[0:self.memorySize] = self.memory
        input[self.memorySize:self.memorySize+3] = c

        output = self.decisionNetwork[-1].run(input)

        return output[0] >= 0

    def copy(self):

        child = Network(self.memorySize, self.memoryUpdateRate, self.mutateStd, self.mutateP, self.memoryHiddenSizes, self.decisionHiddenSizes)

        child.memoryNetwork = [layer.copy(self.mutateStd, self.mutateP) for layer in self.memoryNetwork]
        child.decisionNetwork = [layer.copy(self.mutateStd, self.mutateP) for layer in self.decisionNetwork]

        return child





# network = Network(5, 0.1, 1, 0.1)
# network.updateMemory(np.array([1, 0, 1]), 3)

