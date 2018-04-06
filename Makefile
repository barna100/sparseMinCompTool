all:
	python2.7 tool_v2.py mm.grph mmA.data mmB.data mmC.data
#	python2.7 parse.py graphFile 
#	python2.7 testcase_gen.py ../data_matrices/data.mv ../testing/initialized_data.mv.txt
clean:
	rm out_code
