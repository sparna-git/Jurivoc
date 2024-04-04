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
    parser.add_argument('--o','--output',help='output Graph file directory', required=True,dest='outputFile')
    parser.add_argument('--l','--log',help='Generate output file for each input file',dest='logs')
    parser.add_argument('--g','--graph',help='Path to a Graph file ',type=pathlib.Path,dest='graph')

	# Parse args
    args = parser.parse_args()

    print("Directory Source: {}".format(args.data))
    print("Directory output: {}".format(args.outputFile))

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
    if not os.path.exists(args.logs):
        os.mkdir(args.logs)
    
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
        gIntermediare = os.path.join(args.logs,'result.ttl')
        gOutput.serialize(format="ttl", destination= gIntermediare)
    
    # Call update graph class
    if args.graph :
        updateURIs_Concepts = update_graph(gOutput,args.graph)
        gOutputResult = updateURIs_Concepts.update_uri_concepts()
        if len(gOutputResult) > 0:
            result = os.path.join(args.outputFile,'result.ttl')
            gOutputResult.serialize(format="ttl", destination= result)