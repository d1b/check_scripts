#!/usr/bin/env python
import sqlite3
import os
import datetime

def create_sql_db(db_name):
	conn = sqlite3.connect(db_name +".db")
	cursor = conn.cursor()
	cursor.execute("""create table data(name text, value text, time datetime, unique (name, value, time))""")
	conn.commit()
	cursor.close()

def insert_into_db(db_name, ctxt_list):
	conn = sqlite3.connect(db_name +".db")
	cursor = conn.cursor()
	sql_statement = """insert or ignore into data (name, value, time) VALUES (?, ?, ?)"""
	for name, value, time in ctxt_list:
		cursor.execute(sql_statement, (name, value, time ))
	conn.commit()
	cursor.close()

def query_db(db_name):
	conn = sqlite3.connect(db_name +".db")
	cursor = conn.cursor()
	cursor.execute("select * from data")
	result_q = cursor.fetchall()
	cursor.close()
	for i in result_q:
		print i[0], i[1], i[2]

def get_proc_numbers():
	return [i for i in os.listdir("/proc") if i.isdigit()]

def read_from_a_file(name, type_t):
	f = open(name, "r")
	if type_t == "read":
		data = f.read()
	else:
		data = f.readlines()
	f.close()
	return data

def get_proc_info(procs):
	proc_info = []
	for proc in procs:
		proc_info.append(get_name_ctxt_date(proc))
	return proc_info

def get_total_ctxt():
	stat = read_from_a_file("/proc/stat", "readlines")
	ctxt = [str(i.split(" ")[1]) for i in stat if "ctxt" in i][0]
	date = datetime.datetime.now()
	return "total", int(ctxt), date

def get_name_ctxt_date(proc):
	date = datetime.datetime.now()
	status = read_from_a_file("/proc/" + proc +"/status", "readlines")
	ctxt = 0
	name = "_none_"
	for i in status:
		if not len(i.split("\t")) > 1:
			continue
		data = i.split("\t")[1]
		if "ctxt" in i:
			ctxt += int(data)
		if "Name" in i:
			name = data.replace("\n", "")
	return name, ctxt, date

def get_cpu_time_pid(pid):
	return int(read_from_a_file("/proc/" + pid + "/schedstat", "read").split(" ")[0])

def print_pid_proc_info(process_info_pid, total_ctxt):
	process_info_pid = sorted(process_info_pid, key=lambda proc: proc[0][1])
	for info_proc, pid in process_info_pid:
		pid_cpu_time = get_cpu_time_pid(pid)
		print pid, info_proc[0], info_proc[1], get_percent_out_of_total(info_proc[1], total_ctxt), "cpu time", pid_cpu_time

def get_percent_out_of_total(item, total):
	if item == 0:
		return "0%"
	else:
		return str( round( ( (item * 100.0000) / total), 4) ) + "%"

if __name__ == "__main__":
	db_name = "ctxt"
	try:
		 create_sql_db(db_name)
	except sqlite3.OperationalError, e:
		pass
		#print e
	procs = get_proc_numbers()
	process_info = get_proc_info(procs)
	total_contex_switches = get_total_ctxt()

	print_pid_proc_info(zip(process_info, procs), total_contex_switches[1])
	print "total context switches =", total_contex_switches[1]

	#add the total ctxt to the process info list before inserting the data into sqlite.
	process_info.append(get_total_ctxt())
	insert_into_db(db_name, process_info)

	#query_db(db_name)
