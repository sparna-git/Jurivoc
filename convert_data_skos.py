import sys
from JurivocData import dataset
from convert_data_graph import convert_graph
import argparse
import pathlib

if __name__ == '__main__':

    directory = sys.argv[1]
    outputFile = sys.argv[2]

    print("Directory Source: {}".format(directory))
    print("Directory output: {}".format(outputFile))

    print("Step 1. Collect of inputs files")
    # #############################################################
    #
    # Generate Dataset
    #
    # Output: result in list type include: Name file and DataFrame
    #
    ###############################################################
    readFiles = dataset(directory)
    # Get Dataset list
    ds = readFiles.read_file()
    
    # Generate result foe each file input
    #print("Step 1.1 Generate output for each input file")
    #for l in ds:
    #    df = l[1]
    #    df.to_csv(l[0]+'.csv',sep="|",index=False)

    # #########################################################
    #
    # Generate Graph
    #
    # Output: save a graph file
    #
    ###########################################################
    print("Step 2. Generate Graph Jurivoc")
    # Instance
    g = convert_graph(ds,outputFile)
    # Call process
    g.graph_process()
    print("3. End process......")