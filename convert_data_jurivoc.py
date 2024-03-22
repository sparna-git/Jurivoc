import os
from JurivocData import dataset
from convert_data_graph import convert_graph
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
    parser.add_argument('--l','--log',help='Generate output file for each input file',dest='files')

	# Parse args
    args = parser.parse_args()

    print("Directory Source: {}".format(args.data))
    print("Directory output: {}".format(args.outputFile))

    print("Step 1. Collect of inputs files")
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
    
    # Generate result for each file input
    if args.files:
		# create folder if it does not exist
        print("Step 1.1 Generate output file for each input")
        if not os.path.exists(args.files):
            os.mkdir(args.files)
        
        for l in ds:
            file = os.path.join(args.files,l[0]+'.csv')
            df = l[1]
            df.to_csv(file,sep="|",index=False)

    # #########################################################
    #
    # Generate Graph
    #
    # Output: save a graph file
    #
    ###########################################################
    print("Step 2. Generate Graph Jurivoc")
    # Instance
    g = convert_graph(ds,args.outputFile)
    # Call process
    g.graph_process()
    print("3. End process......")