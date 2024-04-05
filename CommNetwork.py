
#-----Imports-----#
import numpy as np


class CommNetwork:

    def __init__(self, messageSize):

        self.messageSize = messageSize
        self.Mss = np.zeros((messageSize, messageSize))  # Weights from input message to output message
        self.Mso = np.zeros((1, messageSize))  # Weights from input message to attack signal
        self.Bs = np.zeros(messageSize)  # Bias on output message
        self.Bo = np.zeros((1))  #Bias on attack signal

        self.p = 0.1
        self.std = 0.1

    def copy(self):

        child = CommNetwork(self.messageSize)
        child.Mss = np.copy(self.Mss)
        child.Mso = np.copy(self.Mso)
        child.Bs = np.copy(self.Bs)
        child.Bo = np.copy(self.Bo)

        child.mutate(self.p, self.std)
        return child

    def respond(self, Input = None):

        try:
            return np.dot(self.Mss, Input) + self.Bs
        except:
            return self.Bs

    def getDecision(self, Input):
        return (np.dot(self.Mso, Input) + self.Bo) > 0

    def mutate(self, p, std):

        self.mutateArray(self.Mss, std, p)
        self.mutateArray(self.Mso, std, p)
        self.mutateArray(self.Bs, std, p)
        self.mutateArray(self.Bo, std, p)

    def mutateArray(self, array, std, p):

        selected = np.random.random(array.shape) < p
        array[selected] += np.random.normal(0, std, np.sum(selected))



