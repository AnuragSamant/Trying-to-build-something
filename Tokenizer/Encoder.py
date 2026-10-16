import Tokenizer

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
            singled=Tokenizer.merge(singled,i,res)
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
