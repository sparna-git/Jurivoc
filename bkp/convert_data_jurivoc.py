import os
from JurivocData import dataset
from read_files import dataset as dsJurivoc
from convert_data_graph import convert_graph, update_graph
import argparse
from loggingJurivoc import logging
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
  parser.add_argument('--g','--graph',help='Path to a Graph file ',type=pathlib.Path,dest='graph')

	# Parse args
  args = parser.parse_args()
  print("Start Jurivoc process")

  # Generate Dataset
  logging.info("******************* Read inputs files *******************")
  print("******************* Read inputs files *******************")
  #readFiles = dataset(args.data)
  # Get Dataset list
  #ds = readFiles.read_file()
  
  # Tmp new code
  #dataset = dsJurivoc(args.data)
  #ds = dataset.read_file()

  logging.info("Generate csv dataset for each file input ")
  #if args.files:
    #create folder if it does not exist
  #  if not os.path.exists(args.files):
  #    os.mkdir(args.files)
  #  for l in ds:
  #    file = os.path.join(args.files,l[0]+'.csv')
  #    df = l[1]
  #    df.to_csv(file,sep="|",index=False)
  #    logging.debug("Output csv file generated: {}".format(file))
  #  logging.debug("Generate {} dataset files: ".format(len(ds)))

  logging.info("******************* Generate Graph *******************")
  print("******************* Generate Graph *******************")
  #g = convert_graph(ds,args.outputFile)
  # Call process
  #gOutput = g.graph_process()
    
  ##
  print("Update URIs in Skos:Concept ..")
  # Call update graph class
  updateURIs_Concepts = update_graph(args.outputFile,args.graph)
  updateURIs_Concepts.update_uri_concepts()
  print("End Jurivoc Process........")