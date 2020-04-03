#!/usr/bin/env python3

import os
import csv
import subprocess
import argparse


# Get kubectl ouput

def run_kubectl(command):
    kubectl_labels_list = []
    try:
        process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
        returned_output = process.communicate()[0]
        # print(str(returned_output))
        for line in str(returned_output).split('\n'):
            temp_dict = {}
            # print(line)
            for item in  line.split(','):
                k = item.split("=")[0]
                v = item.split("=")[1]
                # print(k,v)
                if k:
                    if v:
                        temp_dict[k] = v
                    else:
                        temp_dict[k] = 'Null'
            print(temp_dict)
            kubectl_labels_list.append(temp_dict)
    except:
        pass

    # with open('kubectl_host.csv', 'wt') as f:
    print(kubectl_labels_list)
    return kubectl_labels_list


# Compare golden config with kubectl node lables output

def compare_kubectl_out_with_origin_config(original_labels, kube_labels):
    failed_host = []
    for item in original_labels:
        for node in kube_labels:
            if node['kubernetes.io/hostname'] in item.values():
                print(("Label Check for Node={}").format(node['kubernetes.io/hostname']))
                for key in item.keys():
                    if key in node.keys():
                        if item[key] == node[key]:
                            print("PASS", key, node[key])
                        else:
                            failed_host.append(node['kubernetes.io/hostname'])
                            print("FAIL", key, node[key])
                        # else:
                        #     print("Ignore Empty Key", node[key], item[key])
            else:
                msg = "ERROR: HOSTNAME NOT FOUND IN GOLDEN CONFIG"
    print(failed_host)
    return failed_host
            # else:
            #     print("NO")






if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--base_file", help="base file path", required=True)
    parser.add_argument("-k", "--kubeconfig", help="kubeconfig file path", required=True)

    args = parser.parse_args()
    print(args)
    if args.base_file and args.kubeconfig:
        cmd = ("kubectl --kubeconfig={} get nodes --show-labels ").format(args.kubeconfig) + " | awk '{ if(NR>1) print $6}'"
        print(cmd)
        kubectl_op = run_kubectl(cmd)
        # download_files(golden_config_url, 'base_host.csv')

        labels_list = []

        with open(args.base_file,'rt')as f:
            data = csv.reader(f)
            for row in data:
                # print(row)
                temp_dict = {}
                for item in row:
                    k = item.split("=")[0]
                    v = item.split("=")[1]
                    # print(k,v)
                    if k and v:
                        temp_dict[k] = v
            # print(temp_dict)
                labels_list.append(temp_dict)
        # print(labels_list)

        compare_kubectl_out_with_origin_config(labels_list, kubectl_op)

    # print(labels_list)