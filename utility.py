import os
from tqdm import tqdm_notebook as tqdm
import json
import pandas as pd
import numpy as np
from datetime import datetime

## public variables
## some facts of the game. Public variables may be used during the analysis
num_cards = 91


## functions
def load_data(data):
    """
    Load data from requested file. will transform data into list of key-value pair with json load
    
    Arguments:
        data (list): The input of the data variable to store the transformed data.
    
    Returns:
        None
    """
    
    ## check instance
    if not isinstance(data, list):
        print("data must be list")
    ## actual loading
    else:   
        ## show what data files is available
        dirlist = os.listdir(os.getcwd())
        data_files = [fname for fname in dirlist if "_battles.json" in fname ]
        [print(f) for f in data_files]
        
        ## user select data file
        while True:
            date_of_data = input("select a date from data files (YYYY-mm-dd):")
            ## check if the file user selected exists
            if date_of_data+"_battles.json" not in dirlist:
                print ("File not exist")
            else:
                break
            
        print("Initiating data loading for "+date_of_data+"...")
        #### Load Data

        ## Somehow pd.read_json does not load my collected data. 
        ## Pandas throw me a OSError if I do read_json.
        ## I suspect it is due to the large file size of my battles_temp.json 
        ## beacuse I can read half of the file with read_json.

        ## Solution: I am appending each line into a list called data then turn that list into dataframe.
        with open(date_of_data+"_battles.json", "r") as f:
            ## count file length
            file_len = sum(1 for row in f)
            ## set pointer back to the start
            f.seek(0, 0)
            
            ## progress bar
            with tqdm(total=file_len, initial=0) as pbar:
                for idx, line in enumerate(f):
                    try:
                        # load data
                        data.append(json.loads(line))
                        pbar.update()
                    except Exception as e:
                        print(e)
                        print("at line: "+str(idx))
                        print(line)
                        break

                print(str(file_len) + " rows in file. \n" + str(len(data)) + " rows loaded") 
                
def get_PVP(battles_df):
    """
    Get only PVP battles out of all battles
    
    Arguments:
        battles_df (pandas DataFrame): input of the entire dataset from load data
        
    Return:
        PVP_battles_df (pandas DataFrame): Data set with only PVP battles.
    """
    if "type" in battles_df.columns:
        PVP_battles_df = battles_df[battles_df.type == "PvP"]
        PVP_battles_df.reset_index().drop("index", axis = 1)  
        return PVP_battles_df
    else: 
        print("Input dataframe is miss \"type\" column")
    
        
def get_deck(battles_df, team_deck, opponent_deck):
    """
    Get deck columns from input data
    
    Arguments:
        battles_df (pandas DataFrame): input of the entire dataset
        
            
    Returns:
        team_deck: Deck data of team side
        opponent_deck: Deck data of opponent side
    """
    opponent_deck = pd.DataFrame(item for item in battles_df["opponent"].apply(lambda x: [l["id"] for l in x[0]["deck"]]))
    team_deck = pd.DataFrame(item for item in battles_df["team"].apply(lambda x: [l["id"] for l in x[0]["deck"]]))
    return team_deck, opponent_deck

def read_cards():
    # read to get latest file
    dirlist = os.listdir(os.getcwd())
    latest_file_date = max([datetime.strptime(fname.strip("_Cards.csv.csv"), "%Y-%m-%d") for fname in dirlist if "cards.csv" in fname.lower()]).date()
    cards_df = pd.read_csv(str(latest_file_date)+"_Cards.csv.csv")
    print("Cards data read from latest file is \"", str(latest_file_date), "_Cards.csv.csv\" has shape: ",cards_df.shape)
    return cards_df
    
    
def update_cards(battles_df):
    # read to get latest file with read_cards()
    cards_df = read_cards()
    
    ## generate today's date
    today_date = str(datetime.now().date())
    fname = today_date+'_Cards.csv.csv'
    if num_cards > cards_df.shape[0]:
        print("The number of cards in the input match data is larger than number of cards in Cards dictionary file, updating...")
        cards_list = list()
        battles_df["opponent"].apply(lambda x:x[0]["deck"]).apply(lambda x:cards_list.extend(x))
        updated_cards_df = pd.DataFrame(cards_list).drop(["displayLevel","level","requiredForUpgrade","starLevel"],axis = 1).drop_duplicates().reset_index(drop = True)
        updated_cards_df.to_csv(fname,index=False)
        print("Cards dictionary updated under new file name: ", fname, " with shape ", updated_cards_df.shape)
        return updated_cards_df
    return cards_df
    
def cardIdToData(Id):
    cards_df = read_cards()
    if isinstance(Id,list):
        return ([cards_df["name"][cards_df.id == item].values[0] for item in Id])
            #print(Cards["name"][Cards.id == item])
    else:
        return(cards_df["name"][cards_df.id == Id].values[0])