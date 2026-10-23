import Tokenizer
import random
#=======================================NLP===========================================
def matrix(row): #Create a 2D matrix for each word in vocaulary with there embeddings
    embeddings=[] #Create Embedding of each word in vocab
    for i in range(len(row)): #Number of word = Number of row
        ro=[] #4 embedding for each row 
        for j in range(10): #Number of column
            num=random.random() #Genrate a number between 0,1
            ro.append(num) #Add the number to column
        embeddings.append(ro) #Add all column to a row
    return embeddings #Return embeddings

def user_e(us_enc,eov): #Take user input token id
    ret_embed=[] #Save embeeding
    for i in us_enc: #Take a token Id at a time
        ret_embed.append(eov[i]) #Save the token embedding by finding it using token id
    return ret_embed #Return all the fetched embeddings

def weights(): #Weight matrix for user input
    weight=[] #Empty weights
    for i in range(10): #Row = Number of embedding
        col=[] #Col = Weights
        for j in range(10): #Number of neuron point
            ran_wei=random.random()-0.5 #Random weight
            col.append(ran_wei) #Add value to each col
        weight.append(col) #Add value to weight
    return weight #Return weight matrix

def sum_layer(eou,initial): #Find the sum of embeddings
    sum_list=[] #Empty list to save sum
    embed_count=len(eou) #Count number of user embedding
    tc=0 #Temprory variable
    while(tc<embed_count): #Move through each layer of user embedding
        col_count=[] #Save each column sum in one layer of embedding
        for j in range(10): #Column Count
            temp=0 #Find sum of each column
            for i in range(10): #Row count (Used a col count for user embedding layer)
                mult=eou[tc][i]*initial[i][j] #Find result of each embedding * weight
                temp+=mult #Same total sum of one column
            col_count.append(temp) #Add the total sum of column to list
        sum_list.append(col_count) #Add all columns sum for layer to list. One embedding layer at a time
        tc+=1 #Increase row count of embedding
    return sum_list #return the overall sum of each column for embedding in each layer

def ReLU(sums):
    h_calc=[] #New Calculated matrix
    temp=len(sums) #Temprory variable
    tc=0 ##Temprory count variable
    while(tc<temp):
        new=[] #Saving each layer change
        for i in range(10):
            if(sums[tc][i]>0): #Check if value greater than 0
                new.append(sums[tc][i]) #If yes add it
            else:
                new.append(0) #If no replace with 0
        h_calc.append(new) #Add each layer all changed value to main 
        tc+=1
    return h_calc #Return new sum matrix      

def add_layer(intial,relu): #Adding multiple layers on top of each other
    no=int(input("How many hidden layer you want:")) #Number of hidden layer
    no-=1 #Total-1
    new_layer_res=relu #Save old layer result
    weight_history=[] #All weight created
    weight_history.append(intial)
    activation_history=[] #All sum record after ReLU calculation for each layer
    activation_history.append(relu)
    while(no>0):
        wei=weights() #Make new weights
        weight_history.append(wei) #Add new weight to history
        new_sum_layer=sum_layer(new_layer_res,wei) #Add the layer up 
        new_layer_res=ReLU(new_sum_layer) #Convert the sum by ReLU function
        activation_history.append(new_layer_res) #Save the new calculation
        no-=1 #Number of layer -1
    return weight_history, activation_history #Return the weight history and ReLU history

try:
    tra=input("Want to train again Y/N?:") #Ask user to train the model vocab again
    if(tra.casefold()=="y" or tra.casefold()=="yes"):
        choi=input("Want to add new data maually Y/N ?:") #Ask if user want to enter new data or he has done it maunually directly to data.txt
        if(choi.casefold()=="y" or choi.casefold()=="yes"):
            try:
                with open("data.txt","+a",encoding="utf-8") as f:
                    new_da=input("Enter new data:")
                    wri=" "+new_da
                    f.write(wri) #Add new data to file
            except Exception as e:
                print("Issue with file creation.")
                exit()
            resu=Tokenizer.main_f_t() #Call the vocab training part to train new vocab and tell it to ask if user want to increase training loop
            res=resu[0] #Vocab
            amer=resu[1] #All merges
        else:
            resu=Tokenizer.main_f_t(1) #Call the training part amd use default loop soze
            res=resu[0] #Vocab
            amer=resu[1] #All merges
    else:
        resu=Tokenizer.load_tokenizer() #Directly load the training data insted of doing each process again
        print("Data loaded successfully from trainin.json!")
        if(resu):
            res=resu[0] #Vocab
            amer=resu[1] #All merges
        else:
            exit() #Close program
    encode=Tokenizer.encoding(res,amer) #Encode the new data of user
    code=encode[0] #Tokenized id
    dictio=encode[1] #Dictionary of all merge
    #decoder(code,dictio) #Decode the token id back to text
    eov=matrix(res) #Use Voacabulary to create 2D matrix
    eou=user_e(code,eov) #Fetch needed embedding from all embeddings using token ID
    intial=weights() #Createing weight matrix
    sums=sum_layer(eou,intial) #Create a column sum matrix for each embedding
    relu=ReLU(sums)
    new_layer=add_layer(intial,relu)
    print(new_layer[1])
except Exception as e:
    print(e)
    print("Something Went wrong.")