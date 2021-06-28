#import __init__

#from AWS.main import service
import boto3
import urllib3
from prettytable import PrettyTable
#from botocore.exceptions import ClientError


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#zcs_ec2 = service.AwsService('ec2')

#client = zcs_ec2.get_aws_client_sessions()
#resource = zcs_ec2.get_aws_resource_sessions()

region = 'us-west-2'
client = boto3.session.Session().client('ec2', region_name = region)

result = PrettyTable(['Region', 'InstanceType', 'Instances', 'InstanceCPU', 'TotalCPU'])
totalaz_sum = PrettyTable(['Region', 'AZ', 'Instances'])
totalcpu_sum = PrettyTable(['Region', 'SumTotalCPU', 'Instances'])


ec2_spotcap = []
ec2_azcap = []

totalcpu_counter = 0
totalinstance_counter = 0

#import pdb
#pdb.set_trace()

response = client.describe_instances()

if len(response['Reservations']) > 0:

        for reservation in response['Reservations']:
                for instance in reservation['Instances']:

                        try:

                                if instance['State']['Name'] == 'running': # and instance['InstanceLifecycle'] == 'spot':

                                        ec2_occurances = False
                                        az_occurances = False

                                        vcpu = client.describe_instance_types(InstanceTypes=[instance['InstanceType']])['InstanceTypes'][0]['VCpuInfo']['DefaultVCpus']
                                        #vcpu = instance['CpuOptions']['CoreCount'] * instance['CpuOptions']['ThreadsPerCore']

                                        for spot in ec2_spotcap:

                                                if spot['InstanceType'] == instance['InstanceType']:

                                                        spot['Instances'] += 1
                                                        spot['TotalCPU'] += vcpu

                                                        break

                                if not ec2_occurances:

                                        ec2_spotcap.append({'Region': region, 'Instancetype': instance['InstanceType'],
                                    'Instances': 1, 'TotalCPU': vcpu})

                                for az in ec2_azcap:

                                        if az['AZ'] == instance['Placement']['AvailabilityZone']:

                                                az['Region'] = region
                                                az['Instances'] += 1

                                                az_occurances =  True

                                                break

                                if not az_occurances:

                                        ec2_azcap.append({'Region': region, 'AZ': instance['Placement']['AvailabilityZone'],
                                  'Instances': 1})

                        except:

                                pass

for spot in ec2_spotcap:

        result.add_row([region, spot['InstanceType'], spot['Instances'], int(spot['TotalCPU']/spot['Instances']), spot['TotalCPU']])

        totalcpu_counter += spot['TotalCPU']
        totalinstance_counter += spot['Instances']

if totalcpu_counter > 0:

        totalcpu_sum.add_row([region, totalcpu_counter, totalinstance_counter])

for az in ec2_azcap:

        totalaz_sum.add_row([region, az['AZ'], az['Instances']])


result.sortby = "TotalCPU"
totalaz_sum.sortby = "Instances"
totalcpu_sum.sortby = "Region"

print(result)
print(totalaz_sum)
print(totalcpu_sum)