import boto3, os, time


class Instance:
    """
    * From boto3 doc https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_instances.html#
    The state of the instance, as a 16-bit unsigned integer. The high byte is used for 
    internal purposes and should be ignored. The low byte is set based on the state represented. 
    The valid values are: 0 (pending), 16 (running), 32 (shutting-down), 48 (terminated), 
    64 (stopping), and 80 (stopped).
    """
    INSTANCE_STOPPED = 80
    INSTANCE_RUNNING = 16
    INSTANCE_PENDING = 0
    INSTANCE_SHUTTING_DOWN = 32
    INSTANCE_TERMINATED = 48
    INSTANCE_STOPPING = 64

    def __init__(self,instanceID, type:str = "t3a.nano") -> None:
        self.askedInstanceType = type
        self.WorkerStarted = False
        self.ec2 = boto3.client('ec2')
        self.instanceID = instanceID
        self.publicIP = -1
        self.SyncInfo()

    def CheckAndChangeType(self):
        #now we check if the current instance type is the same that the instance already have, 
        #In don't we need to change it
        if self.GetInfo()['Reservations'][0]['Instances'][0]['InstanceType'] != self.askedInstanceType:
            self.__ChangeType()
            self.SyncInfo()

    def StartInstance(self):
        self.SyncInfo()

        if(self.stateCode == self.INSTANCE_RUNNING):
            self.description = self.ec2.describe_instances(InstanceIds=[self.instanceID])
            self.publicIP  = self.description['Reservations'][0]['Instances'][0]['PublicIpAddress']
            print(f"Instance already running. Public IP of instance {self.instanceID}: {self.publicIP}")   
            return "", self.publicIP

        self.CheckAndChangeType()
        response = self.ec2.start_instances(
            InstanceIds=[
                self.instanceID,
            ],
        )

        print(f"Starting instance {self.instanceID}") 

        self.SyncInfo()

        while self.stateCode != self.INSTANCE_RUNNING:
            self.SyncInfo()
            import time
            time.sleep(3)
            print("still starting... ", self.state)

        self.SyncInfo()

        self.description = self.ec2.describe_instances(InstanceIds=[self.instanceID])
        self.publicIP  = self.description['Reservations'][0]['Instances'][0]['PublicIpAddress']

        print(f"instance {self.instanceID} running :)") 

        # Wait for system to load up maybe 30 secs or 1 minute
        print("waiting for worker to be ready...")
        time.sleep(20)

        self.SyncInfo()
        print(f"Public IP of instance {self.instanceID}: {self.publicIP}")   
        return self.GetInfo(), self.publicIP

    def StopInstance(self):
        response = self.ec2.stop_instances(
            InstanceIds=[
                self.instanceID,
            ],
        )

        print(f"Stopping instance {self.instanceID}") 

        self.SyncInfo()

        while self.stateCode != self.INSTANCE_STOPPED:
            self.SyncInfo()
            import time
            time.sleep(3)
            print("still stopping... ", self.state)

        print(f"instance {self.instanceID} stop :)") 

        print(response) 

    #Private method
    def __ChangeType(self):
        ec2 = boto3.client('ec2')
        response = ec2.modify_instance_attribute(
            InstanceId=self.instanceID,
            InstanceType={
                'Value': self.askedInstanceType
            }
        )
        self.currentInstanceType = self.askedInstanceType
        print(f"Instance type of {self.instanceID} changed to {self.askedInstanceType}.")

    
    def SyncInfo(self):
        self.description = self.ec2.describe_instances(InstanceIds=[self.instanceID])
        self.currentInstanceType = self.description['Reservations'][0]['Instances'][0]['InstanceType']
        self.state = self.description['Reservations'][0]['Instances'][0]['State']["Name"]
        self.stateCode = self.description['Reservations'][0]['Instances'][0]['State']["Code"]
        self.publicDns = self.description['Reservations'][0]['Instances'][0]['PublicDnsName']

    def GetInfo(self):
        self.description = self.ec2.describe_instances(InstanceIds=[self.instanceID])
        return self.description   

    def GetInstanceType(self):
        return self.currentInstanceType
    
    def GetState(self):
        return self.state
    
    def GetStateCode(self):
        return self.stateCode
    
    def GetPublicIP(self):
        return self.publicIP
    

if __name__ == '__main__':
    instanceVulcanScripts = 'i-099dd0e3b02713553'
    vulcanEc2 = Instance(instanceVulcanScripts, "aws_ssm_test.ini")
    vulcanEc2.StartInstance()
    print(vulcanEc2.GetInfo())