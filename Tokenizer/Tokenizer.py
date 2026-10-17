#================================================Tokenizer============================================
#=======================================Vocab creation and saving===========================================
import json

def word_c(text, count):
    words=text.split()
    for i in words:
        char_list=list(i)
        char_list[-1]=char_list[-1]+"</w>"
        wt=tuple(char_list)
        count[wt]=count.get(wt,0)+1

def frequency(word_dict,frequencies):
    for word_tuple,word_count in word_dict.items():
        for i in range(len(word_tuple)-1):
            pair=(word_tuple[i],word_tuple[i+1])
            frequencies[pair]=frequencies.get(pair, 0)+word_count

def pair(frequencies,newg):
    if not frequencies:
        return
    maxv=max(frequencies.values())
    if(maxv<1):
        return
    candidates=[key for key,value in frequencies.items() if value==maxv]
    candidates.sort() 
    newg.append(candidates[0])

def merge(word_dict,best_pair,vocab):
    first, second=best_pair
    # FIX: Agar kisi bhi token ke end mein </w> hai, toh use properly handle karein
    if("</w>" in first):
        # Standard BPE mein aamtaur par word ke bich mein </w> nahi aata, 
        # par agar first mein hai, toh use clean karein
        combined=first.replace("</w>", "")+second
    elif("</w>" in second):
        # Agar second token mein </w> hai (jaise 'g</w>'), toh use naye word ke end mein shift karein
        combined=first+second.replace("</w>", "")+"</w>"
    else:
        # Normal characters ke liye normal merge
        combined=first+second
    if(combined not in vocab):
        vocab.append(combined)
    new_word_dict={}
    for word_tuple, word_count in word_dict.items():
        new_word=[]
        i=0
        while(i < len(word_tuple)):
            if(i<len(word_tuple)-1 and word_tuple[i]==first and word_tuple[i+1]==second):
                new_word.append(combined)
                i+=2
            else:
                new_word.append(word_tuple[i])
                i+=1
        merged_word = tuple(new_word)
        new_word_dict[merged_word] = new_word_dict.get(merged_word, 0) + word_count
    return new_word_dict

def save_tokenizer(vocab, all_merge, filename="training.json"):
    serializable_merges=[list(pair) for pair in all_merge]
    data = {
        "vocab": vocab,
        "all_merge": serializable_merges
    }
    with open(filename,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=4)
    print(f"Tokenizer vocabulary and merges successfully saved to {filename}!")

def load_tokenizer(filename="training.json"):
    with open(filename,"r",encoding="utf-8") as f:
        data = json.load(f)
    if(data):
        all_merge=[tuple(pair) for pair in data["all_merge"]]
        vocab=data["vocab"]
        print(f"Data loaded successfully from {filename}!")
        return vocab,all_merge
    else:
        print("Training data not exists.")

def tokenize(text,ittretion=150):
    word_dict={}
    word_c(text,word_dict)
    base_chars=set()
    words=text.split()
    for w in words:
        for char in w:
            base_chars.add(char)
    for word_tuple in word_dict.keys():
        base_chars.add(word_tuple[-1])
    vocab=sorted(list(base_chars))
    if("<unk>" not in vocab):
        vocab.insert(0,"<unk>")
    all_merge=[]
    for i in range(ittretion):
        frequencies={}
        frequency(word_dict,frequencies)
        if not frequencies:
            break
        newg=[]
        pair(frequencies,newg)
        if newg:
            all_merge.append(newg[0])
            word_dict=merge(word_dict,newg[0],vocab)
    save_tokenizer(vocab,all_merge,filename="training.json")
    return vocab,all_merge

def main():
    with open("data.txt","r",encoding="utf-8") as f:
        text=f.read()
        f.close()
    itt=input("Want to increase iteration Y/N ?:")
    if(itt.casefold()=="y" or itt.casefold()=="yes"):
        num=int(input("Enter new iteration:"))
        return tokenize(text,num)
    else:
        return tokenize(text)

#=======================================Encoding and embeding of data===========================================
def tokenid(ids,deco,res):
    j=0
    for i in res:
        ids[j]=i
        deco[i]=j
        j+=1

def encode_text(amer,res,deco):
    newd=input("Enter data to check:")
    words=newd.split()
    encid=[]
    unk_id=deco.get("<unk>", 0)
    for w in words:
        singled={}
        charl=list(w)
        charl[-1]=charl[-1]+"</w>"
        wt=tuple(charl)
        singled[wt]=1
        for i in amer:
            singled=merge(singled,i,res)
        for j in singled.keys():
            for k in j:
                if k in deco:
                    encid.append(deco[k])
                else:
                    encid.append(unk_id)
    return encid

def encoding(res,amer):
    ids=[None]*(len(res))
    deco={}
    tokenid(ids,deco,res)
    encode=encode_text(amer,res,deco)
    print(encode)
    return encode,deco

#========================================Decoder of embeddings==========================================
def decoder(code,dictio):
    id_to_token={value: key for key, value in dictio.items()}
    dencr=[]
    for i in code:
        token=id_to_token.get(i,"")
        if(token.endswith("</w>")):
            clean_token = token.replace("</w>"," ")
            dencr.append(clean_token)
        else:
            dencr.append(token)
    final_text="".join(dencr)
    print(final_text)

try:
    choi=input("Want to add new data to train Y/N ?:")
    if(choi.casefold()=="y" or choi.casefold()=="yes"):
        try:
            with open("data.txt","+a",encoding="utf-8") as f:
                new_da=input("Enter new data:")
                wri=" "+new_da
                f.write(wri)
                f.close()
        except Exception as e:
            print("Issue with file creation.")
            exit()
        resu=main()
        res=resu[0]
        amer=resu[1]
    else:
        resu=load_tokenizer()
        if(resu):
            res=resu[0]
            amer=resu[1]
        else:
            exit()
    encode=encoding(res,amer)
    code=encode[0]
    dictio=encode[1]
    decoder(code,dictio)
except Exception as e:
    print("Something Went wrong.")
#==================================================================================
#==================================================================================