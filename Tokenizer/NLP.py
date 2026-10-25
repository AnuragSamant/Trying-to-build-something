import Tokenizer
import random
import math

#=======================================NLP===========================================
def matrix(row): #Create a 2D matrix for each word in vocaulary with there embeddings
    embeddings=[] #Create Embedding of each word in vocab
    for i in range(len(row)): #Number of word = Vocab size
        ro=[] #4 embedding for each row 
        for j in range(128): #Number of column
            num=random.random() #Genrate a number between 0,1
            ro.append(num) #Add the number to column
        embeddings.append(ro) #Add all column to a row
    return embeddings #Return embeddings

def user_e(us_enc,eov): #Take user input token id
    ret_embed=[] #Save embeeding
    for i in us_enc: #Take a token Id at a time
        ret_embed.append(list(eov[i]))
    return ret_embed #Return all the fetched embeddings

def positional_encoding(eoo):#Updating each row value by 0.01 to encode the value and give them a position
    for i in range(len(eoo)):
        for j in range(128):
            eoo[i][j]+=i*0.01 
    return eoo

def weights(res,input_d=128): #Weight matrix for user input based on last hidden layer
    weight=[] #Empty weights
    for i in range(input_d): #Row = Number of vocab col
        col=[] #Col = Weights
        for j in range(len(res)): #Vocb Size
            ran_wei=random.random()-0.5 #Random weight
            col.append(ran_wei) #Add value to each col
        weight.append(col) #Add value to weight
    return weight #Return weight matrix

def hidden_weights(row,col): #Weight matrix for Hidden layers
    weight=[]
    for i in range(row): #Row=128/512
        cols=[]
        for j in range(col): #Col=128/512
            cols.append(random.random()-0.5) #Random nuber from -0.5 to 0.5
        weight.append(cols)
    return weight #Return 128 by 128 Random number matrix

def sum_layer(eou,initial): #Find the sum of embeddings
    sum=[]
    for i in range(len(eou)): #lentgh of user embeddings or n
        col_sum=[]
        for j in range(len(initial[0])): #128 or 512 Col
            temp=0
            for k in range(len(eou[0])): #128 or 512 Row/Col
                temp+=eou[i][k]*initial[k][j] #For each row of user embedding into each column of weight matrix
            col_sum.append(temp) #Add the result to a a row index i 
        sum.append(col_sum) #Add the whole row into list
    return sum #Return n by 128 matrix

def ReLU(sums):
    h_calc=[] #New Calculated matrix
    temp=len(sums) #Temprory variable
    tc=0 ##Temprory count variable
    while(tc<temp):
        new=[] #Saving each layer change
        for i in range(len(sums[tc])):
            if(sums[tc][i]>0): #Check if value greater than 0
                new.append(sums[tc][i]) #If yes add it
            else:
                new.append(0) #If no replace with 0
        h_calc.append(new) #Add each layer all changed value to main 
        tc+=1
    return h_calc #Return new sum matrix      

def add_layer(initial,relu): #Adding multiple layers on top of each other
    no=int(input("How many hidden layer you want:")) #Number of hidden layer
    no-=1 #Total-1
    new_layer_res=relu #Save old layer result
    weight_history=[] #All weight created
    weight_history.append(initial)
    activation_history=[] #All sum record after ReLU calculation for each layer
    activation_history.append(relu)
    expan=512
    temp=0
    while(no>0):
        if(temp==0):
            wei=hidden_weights(128,expan) #Expanding each even layer
            weight_history.append(wei) #Add new weight to history
            new_sum_layer=sum_layer(new_layer_res,wei) #Add the layer up 
            new_layer_res=ReLU(new_sum_layer) #Convert the sum by ReLU function
            activation_history.append(new_layer_res) #Save the new calculation
            temp=1
        else:
            wei=hidden_weights(expan,128) #Contracting odd layers
            weight_history.append(wei) #Add new weight to history
            new_sum_layer=sum_layer(new_layer_res,wei) #Add the layer up 
            new_layer_res=ReLU(new_sum_layer) #Convert the sum by ReLU function
            activation_history.append(new_layer_res) #Save the new calculation
            temp=0
        no-=1 #Number of layer -1
    return weight_history, activation_history, new_layer_res #Return the weight history and ReLU history

def final_layer(new_layer_res,res): #Creating the final layer
    vocab_weights=weights(res,len(new_layer_res[0])) # 128 x vocab_size or 512 x vocab_size to map back to words or weight matrix for final layer 
    f_o=[]
    for i in range(len(new_layer_res)): #Number of row in last hidden layer
        col_sum=[]
        for j in range(len(res)): #Number of row in voacbulary size
            temp=0
            for k in range(len(new_layer_res[0])): #Row/Column range 0 to 128 or 0 to 512
                temp+=new_layer_res[i][k]*vocab_weights[k][j] #For each row in last hidden layer into each column of final layer weight matrix.
            col_sum.append(temp)
        f_o.append(col_sum)
    return f_o #Return a number of user input by number of vocabulary row matrix

def softmax(final_l): #Change result to probability
    prob=[]
    for i in final_l: #All element in first row
        maxv=max(i) #Find max value in row
        expo_row=[]
        for j in i: #For each element in first row
            chan=j-maxv #Difference in each element by value-max
            val=math.exp(chan) # Safely calculates e^(val)
            expo_row.append(val) #Add to the row ith index
        sum_expo=sum(expo_row) #Add up all value created
        probabilities=[val / sum_expo for val in expo_row] #Change the new value to probability
        prob.append(probabilities) #Add that probability
    return prob #Return probability matrix

def arg_deco(soft,eou,res): #Use to create output layer
    p_w=[]
    for j in range(len(eou)): #For each elsement in user input
        max=soft[j][0] #At index 0 of probability
        temp=0
        for i in range(len(soft[j])): #Lentgh of all probability
            if(soft[j][i]>max): #If new high probability save it and it's index
                max=soft[j][i]
                temp=i
        p_w.append(res[temp]) #Add the value at that index from vocab
    return p_w #Return guessed word as token id

try:
    tra=input("Want to train again Y/N?:") #Ask user to train the model vocab again
    if(tra.casefold()=="y" or tra.casefold()=="yes"):
        choi=input("Want to add new data maually Y/N ?:") #Ask if user want to enter new data or he has done it maunually directly to data.txt
        if(choi.casefold()=="y" or choi.casefold()=="yes"):
            try:
                with open("C:/Programing/Project/Training/data.txt","+a",encoding="utf-8") as f:
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
    eoo=user_e(code,eov) #Fetch needed embedding from all embeddings using token ID
    eou=positional_encoding(eoo)
    initial=hidden_weights(128,128) #Createing weight matrix
    sums=sum_layer(eou,initial) #Create a column sum matrix for each embedding
    relu=ReLU(sums)
    new_layer=add_layer(initial,relu)
    final_l=final_layer(new_layer[2],res)
    soft=softmax(final_l)
    argmax=arg_deco(soft,eou,res)
    print(argmax)
except Exception as e:
    print(e)
    print("Something Went wrong.")