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
        new_word_dict[tuple(new_word)]=word_count
    return new_word_dict

def tokenize(text):
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
    print(vocab)

    for i in range(21):
        frequencies={}
        frequency(word_dict,frequencies)
        if not frequencies:
            break
        newg=[]
        pair(frequencies,newg)
        if newg:
            word_dict=merge(word_dict,newg[0],vocab)
        print(vocab)
    
