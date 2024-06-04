import pytest
import sys, os
sys.path.insert(1, os.path.join(os.path.dirname(sys.path[0]),  'aws_manager', 'src'))
import Instance


class TestInstance:
    
    #This is a hardcoded instance name to test.
    #You need to create one and replace its id here
    __instanceId = 'i-08cd712152bf41607'
    __defaultType = 't3a.nano'
    
    def ChangeTypeToOriginal(self):
        instance = Instance.Instance(self.__instanceId, self.__defaultType)
        instance.CheckAndChangeType()
    
    def testConnectionToEc2(self):
        self.ChangeTypeToOriginal()
        instance = Instance.Instance(self.__instanceId)
        assert instance.GetInstanceType() == self.__defaultType
        
    def testChangeInstanceType(self):
        instance = Instance.Instance(self.__instanceId, "t2.micro")
        assert instance.GetInstanceType() == self.__defaultType
        instance.CheckAndChangeType()
        assert instance.GetInstanceType() == 't2.micro'
        self.ChangeTypeToOriginal()