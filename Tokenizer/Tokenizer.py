#================================================Tokenizer============================================
#=======================================Vocab creation and saving===========================================
import json

def word_c(text, count):
    words=text.split() #Covert string to List to take each character as word
    for i in words: #Go through each word
        byte_list=list(i.encode("utf-8"))
        if byte_list:
            byte_list[-1]=str(byte_list[-1])+"</w>"
            byte_list[:-1]=[str(b) for b in byte_list[:-1]]
            wt=tuple(byte_list)
            count[wt]=count.get(wt,0)+1 #Add word to a dictionary if exist count+1

def frequency(word_dict,frequencies): #Count how much a character appear in the word dictionary
    for word_tuple,word_count in word_dict.items():
        for i in range(len(word_tuple)-1):
            pair=(word_tuple[i],word_tuple[i+1])
            frequencies[pair]=frequencies.get(pair, 0)+word_count #Check if the pair exist if yes then increase count else add it with its frequency

def pair(frequencies,newg): #Pair the most occuring character together
    if not frequencies: #Check if character's with frequecy exist or not
        return
    maxv=max(frequencies.values()) #Take highest value amoung all value
    if(maxv<1):
        return
    candidates=[key for key,value in frequencies.items() if value==maxv] #Take all the pair with matching highest value
    candidates.sort() 
    newg.append(candidates[0]) #Add them to a list

def merge(word_dict,best_pair,vocab): #Add 2 char or word to make a new one
    first, second=best_pair
    # FIX: Agar kisi bhi token ke end mein </w> hai, toh use properly handle karein
    if("</w>" in first):
        # Standard BPE mein aamtaur par word ke bich mein </w> nahi aata, 
        # par agar first mein hai, toh use clean karein
        combined=first.replace("</w>", "")+","+second
    elif("</w>" in second):
        # Agar second token mein </w> hai (jaise 'g</w>'), toh use naye word ke end mein shift karein
        combined=first+","+second.replace("</w>", "")+"</w>"
    else:
        # Normal characters ke liye normal merge
        combined=first+","+second
    if(combined not in vocab):
        vocab.append(combined)
    new_word_dict={} #Collection of new word
    for word_tuple, word_count in word_dict.items():
        new_word=[]
        i=0
        while(i < len(word_tuple)):
            if(i<len(word_tuple)-1 and word_tuple[i]==first and word_tuple[i+1]==second): #If the combination exist add the combination to new list
                new_word.append(combined)
                i+=2
            else: #Else add a single word
                new_word.append(word_tuple[i])
                i+=1
        merged_word = tuple(new_word) #Convert the new word to tuple
        new_word_dict[merged_word] = new_word_dict.get(merged_word, 0) + word_count #Add new word to a new dictionary if exist icrease count
    return new_word_dict

def save_tokenizer(vocab, all_merge, filename="training.json"): #Save the data of vocabulary and all merge to a file
    serializable_merges=[list(pair) for pair in all_merge]
    data = {
        "vocab": vocab,
        "all_merge": serializable_merges
    }
    with open(filename,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=4)

def load_tokenizer(filename="training.json"): #Load Vocabulary file to Use it 
    with open(filename,"r",encoding="utf-8") as f:
        data = json.load(f)
    if(data):
        all_merge=[tuple(pair) for pair in data["all_merge"]]
        vocab=data["vocab"]
        return vocab,all_merge
    else:
        print("Training data not exists.")

def tokenize(text,ittretion=15000):
    word_dict={} #Dictionary with count of each word
    word_c(text,word_dict)
    base_chars=set() #Keep only unique characters
    for word_tuple in word_dict.keys():
        for item in word_tuple:
            base_chars.add(item)
    vocab=sorted(list(base_chars)) #Sort all unique characters
    if("<unk>" not in vocab):
        vocab.insert(0,"<unk>") #<unk> if the word is not in vocubaluary
    all_merge=[] #All posible combinations
    for i in range(ittretion):
        frequencies={}
        frequency(word_dict,frequencies) #How much time a word/character appair
        if not frequencies:
            break
        newg=[]
        pair(frequencies,newg) #Frequent character which were together are merged together
        if newg:
            all_merge.append(newg[0])
            word_dict=merge(word_dict,newg[0],vocab) #Update the word dictionary with new words
    save_tokenizer(vocab,all_merge,filename="training.json") #Save Vocabulary and all merges to a JSON file
    print("Tokenizer vocabulary and merges are successfully updated saved to training.json!")
    return vocab,all_merge #Return Vocabulary and All merges

def main_f_t(coi_check=0): #Main funtion to create a vocab and use it
    try: #Opens the data.txt file to train the vocabulary
        with open("data.txt","r",encoding="utf-8") as f:
            text=f.read()
        if(coi_check==0): #Works if user has choosen to input new data manually
            itt=input("Want to increase iteration Y/N ?:")
            if(itt.casefold()=="y" or itt.casefold()=="yes"):
                num=int(input("Enter new iteration:"))
                return tokenize(text,num)
            else:
                return tokenize(text)
        else:
            return tokenize(text)
    except Exception as e:
        print("Issue with file.")
        exit()

#=======================================Encoding and embeding of data===========================================
def tokenid(deco,res): #Save each word of vocabulary into a dictionary with a sequentianal number/index.
    for j,i in enumerate(res):
        deco[i]=j

def encode_text(amer,res,deco): #Toknize user input
    newd=input("Enter data to check:")
    words=newd.split()
    encid=[] #Empty list to print toknized value
    for w in words:
        singled={} #A Empty dictionary to store word with there index
        byte_list=list(w.encode("utf-8"))
        if byte_list:
            byte_list[-1]=str(byte_list[-1])+"</w>"
            byte_list[:-1]=[str(b) for b in byte_list[:-1]]
            wt=tuple(byte_list)
            singled[wt]=1
        for i in amer:
            singled=merge(singled,i,res) #Add word to dictionary with there index in vocabulary if word not exist return character which match
        for j in singled.keys():
            for k in j:
                if k in deco:
                    encid.append(deco[k]) #Add there index to the list
                else:
                    encid.append(deco.get(k,0)) #Add 0 if word/char not exist 
    return encid

def encoding(res,amer): #Tokenize vocabulary and user input
    deco={}
    tokenid(deco,res)
    encode=encode_text(amer,res,deco)
    print(encode)
    return encode,deco

#========================================Decoder of value==========================================
'''def decoder(code,dictio): #Decode the token id genrated
    id_to_token={value: key for key, value in dictio.items()} #Reverse the dictionary where all vocabulary is saved with a idex so that index become key
    dencr=[] #Add Text to list
    byte_accumulator=[] #Save numbers
    for i in code:
        token=id_to_token.get(i,"") #If id exisr return wrod else ""
        if(token=="<unk>"):
            if(byte_accumulator): #Check if there is any number
                dencr.append(bytes(byte_accumulator).decode("utf-8", errors="replace")) #Change number to word
                byte_accumulator=[]
            dencr.append("<unk>") #Add <unk> for new word
            continue
        clean_token=token.replace("</w>","")
        parts=clean_token.split(",")
        for p in parts:
            if(p.isdigit()):
                byte_accumulator.append(int(p)) #Add int to a list
        is_end=token.endswith("</w>")
        if(is_end):
            decoded_word=bytes(byte_accumulator).decode("utf-8", errors="replace")+" " #Change number to word
            dencr.append(decoded_word) #Add decoded word
            byte_accumulator=[]
    if(byte_accumulator):
        dencr.append(bytes(byte_accumulator).decode("utf-8", errors="replace")) #Change number to word and add it to list
    final_text="".join(dencr).strip() #Final formed word
    print(final_text)'''
#==================================================================================
#==================================================================================

'''-----------------------------------------------------------------------------------------------------------------------------------------'''
