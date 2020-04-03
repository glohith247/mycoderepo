from __future__ import print_function

from pssh.clients import ParallelSSHClient
import pandas as pd
import pymysql
from sqlalchemy import create_engine
# from flask import Flask, jsonify, request
from flask import *
from flask_restful import reqparse
import os, hashlib, urllib2
from datetime import datetime
from multiprocessing import Process

app = Flask(__name__)
parser = reqparse.RequestParser()

## Global params
# hosts = ['10.205.137.236']
ORIGINAL_FILE_MD5_MAP = {
    '/etc/hosts' :   'https://gist.github.com/deepak7093/2067ca7203e1a7df8217e5808048cb9d',
    '/etc/resolv.conf' : 'https://gist.github.com/deepak7093/2067ca7203e1a7df8217e5808048cb9d'
}

CLUSTERS = {
    'rc1' : ['13.234.49.74', '37.20.1.22'],
    'cluster2' : ['13.234.49.74']
}
TIMEOUT_HOSTS = []
files = ["/etc/hosts", "/etc/resolv.conf"]

DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_USER = 'root'
DB_PASS = 'password'
DB_NAME = 'test'
TABLE_NAME = 'file_check'

DB_CONN = ('mysql+pymysql://{}:{}@{}/{}').format(DB_USER, DB_PASS, DB_HOST, DB_NAME)


############## START cluster helper functions ####################
def _fetch_single_cluster_record(cluster):
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    query_result = []
    with con: 
        cur = con.cursor()
        query = ("SELECT * FROM {} where cluster='{}'").format(TABLE_NAME, cluster)
        cur.execute(query)
        rows = cur.fetchall()

        # print("rows", rows)
        # for row in rows:
        #     sample = {}
        #     sample['filepath'] = row[0]

            # print("{0} {1} {2} ".format(row[0], row[1], row[2]))
        #     query_result.append(sample)
        # print(query_result)
    return rows



def _fetch_single_cluster_files_record(host, cluster):
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    sample = []
    with con: 
        cur = con.cursor()
        query = ("SELECT filepath FROM {} where host='{}' and cluster='{}'").format(TABLE_NAME, host, cluster)
        cur.execute(query)
        rows = cur.fetchall()
        
        # print("rows", rows)
        for row in rows:
            r = list(row)
            if r[0] not in sample:
                sample.append(r[0])
    return sample


def _fetch_single_cluster_state_record(host, cluster, filepath):
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    sample = []
    with con: 
        cur = con.cursor()
        query = ("SELECT state FROM {} where host='{}' and cluster='{}' and filepath='{}'").format(TABLE_NAME, host, cluster, filepath)
        cur.execute(query)
        rows = cur.fetchall()
        
        # print("rows", rows)
        for row in rows:
            r = list(row)
            if r[0] not in sample:
                sample.append(r[0])
        if len(sample) == 1:
            return sample[0]
        else: 
            return "OK"

def _fetch_single_cluster_timestamp_record(host, cluster, filepath):
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    sample = []
    with con: 
        cur = con.cursor()
        query = ("SELECT timestamp FROM {} where host='{}' and cluster='{}' and filepath='{}'").format(TABLE_NAME, host, cluster, filepath)
        cur.execute(query)
        rows = cur.fetchall()
        
        # print("rows", rows)
        for row in rows:
            r = list(row)
            if r[0] not in sample:
                sample.append(r[0])
        if len(sample) == 1:
            return sample[0]
        else: 
            return datetime.now().strftime("%d-%b-%Y %H:%M:%S")
############## END cluster helper functions ######################

############## START single server/host helper functions ####################

def _fetch_single_host_record(host, cluster):
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    query_result = []
    with con: 
        cur = con.cursor()
        query = ("SELECT * FROM {} where host='{}' and cluster='{}'").format(TABLE_NAME, host, cluster)
        cur.execute(query)
        rows = cur.fetchall()

        # print("rows", rows)
        # for row in rows:
        #     sample = {}
        #     sample['filepath'] = row[0]

            # print("{0} {1} {2} ".format(row[0], row[1], row[2]))
        #     query_result.append(sample)
        # print(query_result)
    return rows



def _fetch_single_host_files_record(host, cluster):
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    sample = []
    with con: 
        cur = con.cursor()
        query = ("SELECT filepath FROM {} where host='{}' and cluster='{}'").format(TABLE_NAME, host, cluster)
        cur.execute(query)
        rows = cur.fetchall()
        
        # print("rows", rows)
        for row in rows:
            r = list(row)
            if r[0] not in sample:
                sample.append(r[0])
        return sample



def _fetch_single_host_state_record(host, cluster, filepath):
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    sample = []
    with con: 
        cur = con.cursor()
        query = ("SELECT state FROM {} where host='{}' and cluster='{}' and filepath='{}'").format(TABLE_NAME, host, cluster, filepath)
        cur.execute(query)
        rows = cur.fetchall()
        
        # print("rows", rows)
        for row in rows:
            r = list(row)
            if r[0] not in sample:
                sample.append(r[0])
        if len(sample) == 1:
            return sample[0]
        else: 
            return "OK"


def _fetch_single_host_timestamp_record(host, cluster, filepath):
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    sample = []
    with con: 
        cur = con.cursor()
        query = ("SELECT timestamp FROM {} where host='{}' and cluster='{}' and filepath='{}'").format(TABLE_NAME, host, cluster,filepath)
        cur.execute(query)
        rows = cur.fetchall()
        
        # print("rows", rows)
        for row in rows:
            r = list(row)
            if r[0] not in sample:
                sample.append(r[0])
        if len(sample) == 1:
            return sample[0]
        else: 
            return datetime.now().strftime("%d-%b-%Y %H:%M:%S")
############## END single server/host helper functions ####################

def _get_remote_md5_sum(url, max_file_size=100*1024*1024):
    print("URL", url)
    remote = urllib2.urlopen(url)
    hash = hashlib.md5()

    total_read = 0
    while True:
        data = remote.read(4096)
        total_read += 4096

        if not data or total_read > max_file_size:
            break

        hash.update(data)

    return hash.hexdigest()



def _check_remote_md5(host, filepath, origin_md5, cluster, last_state, last_timestamp):
    
    print("input", host, filepath, origin_md5, cluster, last_state)

    ips = []
    ips.append(host)
    # client = ParallelSSHClient(ips, user='root',password='directv1', port=22,timeout=10,num_retries=0)
    client = ParallelSSHClient(ips, pkey='~/Downloads/vt-dev-new.pem', user='ubuntu', port=22,timeout=10,num_retries=0)

    final_md5 = []
    result = {}
    if filepath == "/etc/hosts":
        cmd = ("md5sum {} | cut -d' ' -f1").format(filepath)

    if filepath == "/etc/resolv.conf":
        # pattern = "172.17.0.2   9930cf889e1f"
        cmd = '''
            rm -rf patterns.txt
            wget https://gist.githubusercontent.com/deepak7093/ad2e3208db975d95f5364d97269fb27d/raw/b23eb4cd5e6a7f8bcc28b2ae9581c1417df5af45/patterns.txt
            #declare -a arr=("nameserver 175.100.191.221" "domain domain.name")
            # for ele in "${arr[@]}"
            IFS=$'\n'
            while read -r line
            do
                    echo $line
            grep -q $line /etc/resolv.conf --color
            if [[ $? -eq 0 ]]; then
            echo 0
            else
            echo 1
            fi
            done < patterns.txt'''
        print("cmdin", cmd)
        # cmd = ("grep -wq '{}' {}; echo $?").format(pattern, filepath)
    try:
        print("cmd", cmd)
        output = client.run_command(cmd)
        print(output)
        for host, host_output in output.items():
            for line in host_output.stdout:
                print("line", line)
                if last_state and last_timestamp:
                    if filepath == "/etc/hosts":
                        if str(line) == origin_md5 and last_state == "NOT OK":
                        # if str(line) == "5372dc3c44762b6927606ca093c4efd9":
                            result['host'] = host
                            result['filepath'] = filepath
                            result['state'] = "OK"
                            result['cluster'] = cluster
                            result['timestamp'] = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
                            result['last_check'] = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
                        elif str(line) != origin_md5 and last_state == "OK":
                            result['host'] = host
                            result['filepath'] = filepath
                            result['state'] = "NOT OK"
                            result['cluster'] = cluster
                            result['timestamp'] = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
                            result['last_check'] = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
                        else:
                            result['host'] = host
                            result['filepath'] = filepath
                            result['state'] = last_state
                            result['cluster'] = cluster
                            result['timestamp'] = last_timestamp
                            result['last_check'] = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
                    elif filepath == "/etc/resolv.conf":  
                        print("in resolv_chec")
                        if str(line) == "0" and last_state == "NOT OK":
                        # if str(line) == "5372dc3c44762b6927606ca093c4efd9":
                            result['host'] = host
                            result['filepath'] = filepath
                            result['state'] = "OK"
                            result['cluster'] = cluster
                            result['timestamp'] = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
                            result['last_check'] = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
                        elif str(line) == "1" and last_state == "OK":
                            result['host'] = host
                            result['filepath'] = filepath
                            result['state'] = "NOT OK"
                            result['cluster'] = cluster
                            result['timestamp'] = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
                            result['last_check'] = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
                        else:
                            result['host'] = host
                            result['filepath'] = filepath
                            result['state'] = last_state
                            result['cluster'] = cluster
                            result['timestamp'] = last_timestamp
                            result['last_check'] = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
                else:
                    result['host'] = host
                    result['filepath'] = filepath
                    result['state'] = "OK"
                    result['cluster'] = cluster
                    result['timestamp'] = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
                    result['last_check'] = datetime.now().strftime("%d-%b-%Y %H:%M:%S")

            final_md5.append(result)
        print("md5sum", final_md5)
        return final_md5
    except Exception as e:
        if host not in TIMEOUT_HOSTS:
            TIMEOUT_HOSTS.append(host)
        pass
    finally:
        return final_md5


@app.route('/server', methods=['GET', 'POST'])
def get_server_info():
        if request.method == 'GET':
            json_data = request.get_json(force=True)
            print("json", json_data)
            hostname = json_data['hostname']
            cluster  = json_data['cluster']
            result = _fetch_single_host_record(hostname, cluster)
            if len(result) != 0:  
                return {
                "Status" : 200,
                "msg": result
                    }
            else:
                return {
                "Status" : 404,
                "msg": "No record found for hostname"
                }

        if request.method == 'POST':
            update_count = 0
            insert_count = 0
            output = []
            json_data = request.get_json(force=True)
            hostname = json_data['hostname']
            cluster  = json_data['cluster']
            curr_files = _fetch_single_host_files_record(hostname, cluster)
            # print("curr_list", list(curr_files))

            for file in files:
                ### Insert directly for new files
                if file not in list(curr_files):
                    original_md5 = _get_remote_md5_sum(ORIGINAL_FILE_MD5_MAP[file])
                    print("original_md5",original_md5)
                    last_state = _fetch_single_host_state_record(hostname, cluster, file)
                    last_timestamp = _fetch_single_host_timestamp_record(hostname, cluster, file)
                    result = _check_remote_md5(hostname, file, original_md5, cluster,last_state, last_timestamp)

                    ## insert records
                    frame = pd.DataFrame.from_dict(result,orient='columns')
                    # print("FRAME", frame)
                    sqlEngine = create_engine(DB_CONN,pool_recycle=3600)
                    conn = sqlEngine.connect()
                    frame.to_sql(TABLE_NAME, conn, schema=None, if_exists='append', index=True, index_label=None, chunksize=None, dtype=None)
                    conn.close()
                    insert_count = insert_count + 1
                    msg = ("Successfully added {}  and updated {} record/s to table {}").format(insert_count, update_count, TABLE_NAME)
                    # return {
                    #     "Status" : 200,
                    #     "msg": msg
                    #     }
                else:
                    original_md5 = _get_remote_md5_sum(ORIGINAL_FILE_MD5_MAP[file])
                    print("original_md5",original_md5)
                    last_state = _fetch_single_host_state_record(hostname, cluster, file)
                    last_timestamp = _fetch_single_host_timestamp_record(hostname, cluster, file)
                    result = _check_remote_md5(hostname, file, original_md5, cluster, last_state, last_timestamp)
                    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
                    for op in result:
                        with con:
                            cur = con.cursor()
                            print("in update")
                            # print(op['state'])
                            # print (op['cluster'])
                            # print(op['host'])
                            # print(op['filepath'])
                            query = ("UPDATE  {} SET state='{}', timestamp='{}', last_check='{}' where filepath='{}' and host='{}' and cluster='{}'").format(TABLE_NAME,op['state'],op['timestamp'],op['last_check'], op['filepath'],op['host'], op['cluster'])
                            print(query)
                            cur.execute(query)
                            update_count = update_count + 1
                            # _update_data(op['host'], op['status'], op['state'], op['filepath'])
                    msg = ("Successfully added {}  and updated {} record/s to table {}").format(insert_count, update_count, TABLE_NAME)
        timeout_host = process_timeout_host(TIMEOUT_HOSTS)
        return {
                        "status" : 200,
                        "msg": msg,
                        "timeout_host_count": timeout_host,
                        "timeout_hosts": [TIMEOUT_HOSTS]
                }


@app.route('/cluster', methods=['GET', 'POST'])
def get_cluster_info():
        if request.method == 'GET':
            json_data = request.get_json(force=True)
            print("json", json_data)
            cluster  = json_data['cluster']
            result = _fetch_single_cluster_record(cluster)
            if len(result) != 0:  
                return {
                "Status" : 200,
                "msg": result
                    }
            else:
                return {
                "Status" : 404,
                "msg": "No record found for cluster"
                }

        if request.method == 'POST':
            update_count = 0
            insert_count = 0
            output = []
            json_data = request.get_json(force=True)
            cluster  = json_data['cluster']
            try:
                for hostname in CLUSTERS[cluster]:
                    curr_files = _fetch_single_cluster_files_record(hostname, cluster)
                    print("curr", curr_files)
                    for file in files:
                        ### Insert directly for new files
                        if file not in list(curr_files):
                            last_state = _fetch_single_cluster_state_record(hostname, cluster, file)
                            last_timestamp = _fetch_single_cluster_timestamp_record(hostname, cluster, file)
                            original_md5 = _get_remote_md5_sum(ORIGINAL_FILE_MD5_MAP[file])
                            print("original_md5",original_md5)

                            result = _check_remote_md5(hostname, file, original_md5, cluster, last_state, last_timestamp)

                            ## insert records
                            frame = pd.DataFrame.from_dict(result,orient='columns')
                            # print("FRAME", frame)
                            sqlEngine = create_engine(DB_CONN,pool_recycle=3600)
                            conn = sqlEngine.connect()
                            frame.to_sql(TABLE_NAME, conn, schema=None, if_exists='append', index=True, index_label=None, chunksize=None, dtype=None)
                            conn.close()
                            print("here")
                            insert_count = insert_count + 1
                            msg = ("Successfully added {}  and updated {} record/s to table {}").format(insert_count, update_count, TABLE_NAME)
                            # return {
                            #     "Status" : 200,
                            #     "msg": msg
                            #     }
                        else:
                            original_md5 = _get_remote_md5_sum(ORIGINAL_FILE_MD5_MAP[file])
                            print("original_md5",original_md5)
                            last_state = _fetch_single_cluster_state_record(hostname, cluster, file)
                            last_timestamp = _fetch_single_cluster_timestamp_record(hostname, cluster, file)
                            result = _check_remote_md5(hostname, file, original_md5, cluster, last_state, last_timestamp)
                            if len(result) != 0:
                                con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
                                for op in result:
                                    with con:
                                        cur = con.cursor()
                                        print("in update")
                                        # print(op['state'])
                                        # print (op['cluster'])
                                        # print(op['host'])
                                        # print(op['filepath'])


                                        query = ("UPDATE  {} SET state='{}', timestamp='{}', last_check='{}' where filepath='{}' and host='{}' and cluster='{}'").format(TABLE_NAME,op['state'], op['timestamp'], op['last_check'], op['filepath'],  op['host'], op['cluster'])
                                        print(query)
                                        cur.execute(query)
                                        print("update here")
                                        update_count = update_count + 1
                                        # _update_data(op['host'], op['status'], op['state'], op['filepath'])
                            msg = ("Successfully added {}  and updated {} record/s to table {}").format(insert_count, update_count, TABLE_NAME)
                            pass
            except Exception as e:
                print(e)
                msg = "cluster {} not found".format(cluster)
                pass
        timeout_host = process_timeout_host(TIMEOUT_HOSTS)
        return {
                        "status" : 200,
                        "msg": msg,
                        "timeout_host_count": timeout_host,
                        "timeout_hosts": [TIMEOUT_HOSTS]
                }
 ## Sample requets 
 
 # http://localhost:5000/cluster/cluster1?file=/etc/hosts&file=/etc/resolv.conf   
@app.route('/group', methods=['GET', 'POST'])
def get_group_info():
        if request.method == 'GET':
            json_data = request.get_json(force=True)
            print("json", json_data)
            cluster  = json_data['cluster']
            hostnames = json_data['hostname']
            result = _fetch_single_cluster_record(cluster)
            if len(result) != 0:  
                return {
                "Status" : 200,
                "msg": result
                    }
            else:
                return {
                "Status" : 404,
                "msg": "No record found for cluster"
                }

        if request.method == 'POST':
            update_count = 0
            insert_count = 0
            output = []
            json_data = request.get_json(force=True)
            cluster  = json_data['cluster']
            
            for hostname in json_data['hostname']:
                curr_files = _fetch_single_cluster_files_record(hostname, cluster)
                print("curr", curr_files)
                print('hostname', hostname)
                for file in files:
                    ### Insert directly for new files
                    if file not in list(curr_files):
                        last_state = _fetch_single_cluster_state_record(hostname, cluster, file)
                        last_timestamp = _fetch_single_cluster_timestamp_record(hostname, cluster, file)
                        original_md5 = _get_remote_md5_sum(ORIGINAL_FILE_MD5_MAP[file])
                        print("original_md5",original_md5)

                        result = _check_remote_md5(hostname, file, original_md5, cluster, last_state, last_timestamp)

                        ## insert records
                        frame = pd.DataFrame.from_dict(result,orient='columns')
                        # print("FRAME", frame)
                        sqlEngine = create_engine(DB_CONN,pool_recycle=3600)
                        conn = sqlEngine.connect()
                        frame.to_sql(TABLE_NAME, conn, schema=None, if_exists='append', index=True, index_label=None, chunksize=None, dtype=None)
                        conn.close()
                        print("here")
                        insert_count = insert_count + 1
                        msg = ("Successfully added {}  and updated {} record/s to table {}").format(insert_count, update_count, TABLE_NAME)
                        # return {
                        #     "Status" : 200,
                        #     "msg": msg
                        #     }
                    else:
                        original_md5 = _get_remote_md5_sum(ORIGINAL_FILE_MD5_MAP[file])
                        print("original_md5",original_md5)
                        last_state = _fetch_single_cluster_state_record(hostname, cluster, file)
                        last_timestamp = _fetch_single_cluster_timestamp_record(hostname, cluster, file)
                        result = _check_remote_md5(hostname, file, original_md5, cluster, last_state, last_timestamp)
                        if len(result) != 0:
                            con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
                            for op in result:
                                with con:
                                    cur = con.cursor()
                                    print("in update")
                                    # print(op['state'])
                                    # print (op['cluster'])
                                    # print(op['host'])
                                    # print(op['filepath'])


                                    query = ("UPDATE  {} SET state='{}', timestamp='{}', last_check='{}' where filepath='{}' and host='{}' and cluster='{}'").format(TABLE_NAME,op['state'], op['timestamp'], op['last_check'], op['filepath'],  op['host'], op['cluster'])
                                    print(query)
                                    cur.execute(query)
                                    print("update here")
                                    update_count = update_count + 1
                                    # _update_data(op['host'], op['status'], op['state'], op['filepath'])
                        msg = ("Successfully added {}  and updated {} record/s to table {}").format(insert_count, update_count, TABLE_NAME)
        print("TIMEOUT_HOSTS", TIMEOUT_HOSTS)
        timeout_host = process_timeout_host(TIMEOUT_HOSTS)
        return {
                        "status" : 200,
                        "msg": msg,
                        "timeout_host_count": timeout_host,
                        "timeout_hosts": [TIMEOUT_HOSTS]
                }

    
def process_timeout_host(hosts):
    count = 0
    last_check = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    timestamp = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    for host in hosts:
        con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
        with con:
            cur = con.cursor()
            query = ("UPDATE  {} SET state='UNREACHABLE', timestamp='{}', last_check='{}' where  host='{}'").format(TABLE_NAME, timestamp, last_check, host)
            print(query)
            cur.execute(query)
            count = count + 1
    return count
      


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=False)
    # _fetch_data()

