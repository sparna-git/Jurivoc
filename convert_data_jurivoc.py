import os
from JurivocData import dataset
from convert_data_graph import convert_graph, update_graph
import argparse
import pathlib

if __name__ == '__main__':
	
    # Generation of arguments
    parser = argparse.ArgumentParser(
		prog='convert_data_jurivoc',
		description='Converts data Jurivoc in Skos'
	)
	# Add arguments
    parser.add_argument('--d','--data',help='Path to a input file', required=True,type=pathlib.Path,dest='data')
    parser.add_argument('--o','--output',help='output Graph file directory', required=True,dest='output')
    parser.add_argument('--l','--log',help='Generate output file for each input file',dest='logs')
    parser.add_argument('--g','--previousVersion',help='Path to a Graph file ',type=pathlib.Path,dest='previousVersion')

	# Parse args
    args = parser.parse_args()

    print("Directory Source: {}".format(args.data))
    print("Directory output: {}".format(args.output))

    isLogDirectory = os.path.exists(args.output)
    if not isLogDirectory:
      os .makedirs(args.output)
      print("The {} directory is created.".format(args.output))

    isLogsDirectory = os.path.exists(args.logs)
    if not isLogsDirectory:
      os .makedirs(args.logs)
      print("The {} directory is created.".format(args.logs))

    print("Step 1. Parsing input files...")
    # #############################################################
    #
    # Generate Dataset
    #
    # Output: result in list type include: Name file and DataFrame
    #
    ###############################################################
    
    readFiles = dataset(args.data)
    # Get Dataset list
    ds = readFiles.read_file()
    
    # create Log folder
    print("Step 1.1 Generate log output files of dataframes...")
    for l in ds:
        #print(l)
        file = os.path.join(args.logs,l[0]+'.csv')
        df = l[1]
        df.to_csv(file,sep="|",index=False)

    # #########################################################
    #
    # Generate Graph
    #
    # Output: save a graph file
    #
    ###########################################################
    print("Step 2. Generate Jurivoc SKOS graph...")
    #Instance
    g = convert_graph(ds,args.logs)
    # Call process
    gOutput = g.graph_process()
    if len(gOutput) > 0:
        gIntermediare = os.path.join(args.logs,'jurivoc_with_label_uris.ttl')
        gOutput.serialize(format="ttl", destination= gIntermediare)
    
    # Call update graph class
    s = ''
    if args.previousVersion:
        s = args.previousVersion
    else:
        s = ''
    updateURIs_Concepts = update_graph(gOutput,s)
    gOutputResult = updateURIs_Concepts.update_uri_concepts()
    if len(gOutputResult) > 0:
        result = os.path.join(args.output,'jurivvoc.ttl')
        gOutputResult.serialize(format="ttl", destination= result)