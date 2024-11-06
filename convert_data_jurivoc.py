import os
from JurivocData import dataset
from convert_data_graph import convert_graph, update_graph
import argparse
from argparse import ArgumentError
import pathlib
import pandas as pd
from rdflib import Graph

if __name__ == '__main__':
	
    # Generation of arguments
    parser = argparse.ArgumentParser(
        prog='convert_data_jurivoc',
        description='Converts data Jurivoc in Skos', 
        allow_abbrev=False

    )
    #
    # Add arguments
    parser.add_argument('-d','--data',help='Path to a input file', required=True,type=pathlib.Path,dest='data')
    parser.add_argument('-o','--output',help='output Graph file directory', required=True,dest='output')
    parser.add_argument('-l','--log',help='Generate output file for each input file',dest='logs')
    parser.add_argument('-g','--previousVersion',help='Path to a Graph file ',type=pathlib.Path,dest='previousVersion')
    parser.add_argument('-n','--noComplexSubjects',help="No Generate ComplexSubject",required=False,action='store_true',dest='noComplexSubjects')
        
    try:
        # Parse args
        args = parser.parse_args()        
    except ArgumentError as e:
        print(f'Error: {e.args()}')
    

    print('---------------------------------------------')
    print('|    Argument     |     Value    |')
    print('---------------------------------------------')
    for argument in args._get_kwargs():
        print(f'{argument[0].upper()} | {argument[1]}')
    print('---------------------------------------------\n')

    print("Directory Source: {}".format(args.data))
    print("Directory output: {}".format(args.output))

    
    bOutput = os.path.exists(args.output)
    if bOutput == False:
      os .makedirs(args.output)
      print("The {} directory is created.".format(args.output))

    bLogs = os.path.exists(args.logs)
    if bLogs == False:
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
    g = convert_graph(ds,args.logs, args.noComplexSubjects)
    # Call process
    gOutput = g.graph_process()
    if len(gOutput) > 0:
        gIntermediare = os.path.join(args.logs,'jurivoc_with_label_uris.n3')
        gOutput.serialize(format="n3", destination= gIntermediare)
    
    # Call update graph class
    s = ''
    if args.previousVersion:
        s = args.previousVersion
    else:
        s = ''
    updateURIs_Concepts = update_graph(gOutput,s,args.logs,args.noComplexSubjects)
    gOutputResult = updateURIs_Concepts.update_uri_concepts()
    if len(gOutputResult) > 0:
        result = os.path.join(args.output,'jurivoc.n3')
        gOutputResult.serialize(format="n3", destination= result)