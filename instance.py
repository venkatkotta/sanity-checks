import boto3
import urllib3
from prettytable import PrettyTable
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

regions = ['us-west-2']

result = PrettyTable(['Region', 'InstanceType', 'Instances', 'InstanceCPU', 'TotalCPU'])
totalaz_sum = PrettyTable(['Region', 'AZ', 'Instances'])
totalcpu_sum = PrettyTable(['Region', 'SumTotalCPU', 'Instances'])


ec2_cap = []
ec2_azcap = []

totalcpu_counter = 0
totalinstance_counter = 0

for region in regions:

    client = boto3.session.Session().client('ec2', region_name = region)
    response = client.describe_instances()

    if len(response['Reservations']) > 0:

        for reservation in response['Reservations']:

            for instance in reservation['Instances']:

                try:

                    if instance['State']['Name'] == 'running':

                        ec2_occurances = False
                        az_occurances = False

                        vcpu = client.describe_instance_types(InstanceTypes=[instance['InstanceType']])['InstanceTypes'][0]['VCpuInfo']['DefaultVCpus']
                        #vcpu = instance['CpuOptions']['CoreCount'] * instance['CpuOptions']['ThreadsPerCore']

                        for compute in ec2_cap:

                            if compute['InstanceType'] == instance['InstanceType']:

                                compute['Instances'] += 1
                                compute['TotalCPU'] += vcpu

                                break

                    if not ec2_occurances:

                        ec2_cap.append({'Region': region, 'InstanceType': instance['InstanceType'], 'Instances': 1, 'TotalCPU': vcpu})

                    for az in ec2_azcap:

                        if az['AZ'] == instance['Placement']['AvailabilityZone']:

                            az['Region'] = region
                            az['Instances'] += 1

                            az_occurances =  True

                            break

                    if not az_occurances:

                        ec2_azcap.append({'Region': region, 'AZ': instance['Placement']['AvailabilityZone'], 'Instances': 1})

                except Exception as e:
                    print("Exiting the Script.Something is not right, please check the Exception below")
                    print(e)
                    sys.exit()
for compute in ec2_cap:

    result.add_row([region, compute['InstanceType'], compute['Instances'], int(compute['TotalCPU']/compute['Instances']), compute['TotalCPU']])

    totalcpu_counter += compute['TotalCPU']
    totalinstance_counter += compute['Instances']

if totalcpu_counter > 0:

    totalcpu_sum.add_row([region, totalcpu_counter, totalinstance_counter])

for az in ec2_azcap:

    totalaz_sum.add_row([region, az['AZ'], az['Instances']])

result.sortby = "InstanceType"
totalaz_sum.sortby = "Instances"
totalcpu_sum.sortby = "Region"

print(result)
print(totalaz_sum)
print(totalcpu_sum)
