from Precompiler import *


class Relation(object):
    '''
    Description
    ---------------------------------------------------------------------------
    Describes the relationship between two Networks.

    Class Variables
    ---------------------------------------------------------------------------


    Usage
    ---------------------------------------------------------------------------


    '''
    
    def __init__(self,commonID,contribNetwork,recipientNetwork):
        self.type = type
        self.commonID = commonID
        self.contributor = contribNetwork
        self.recipient = giveToNetwork


class MultiNetwork(object):
    '''
    Description
    ---------------------------------------------------------------------------
    A MultiNetwork represents a larger grouping of networks together. If a Network
    represents the zone between two or more real sites, a MultiNetwork represents
    the zones combined and connection configuration between them.

    Class Variables
    ---------------------------------------------------------------------------
    networkTable [List(Of Network)]: A listing of all the networks connected 
    relations [List (Of Relation)]: Table of how Networks are related to each other

    Usage
    ---------------------------------------------------------------------------
    '''
    def __init__(self,netTable,relations):
        self.networkTable = netTable
        self.relations = relations

    def getFaucetNetworks(self):
        '''
        Gets the most upstream networks in the MultiNetwork

        Returns [List(Of Network)]: Highest upstream networks
        '''
        pass
    def getSinkNetwork(self):
        '''
        Gets the most downstream network in the MultiNetwork

        Returns [List(Of Network)]: Most downstream network. Should only be one but,...
        '''
    


