name = 'employment_change'
file_name = 'svgs/'+name+'.svg'
file_name_upd = 'svgs/'+name+'_upd.svg'
fill_opactity = 0.0


with open(file_name,"r") as f:
    data = f.readline()
    data = data.replace('<rect', '<rect fill-opacity="'+str(fill_opactity)+'"')
    data = data.replace('"translate(529.7780354910525,433.9329551941697)"', '"translate(529.7780354910525,442.9329551941697)"')
    data = data.replace('Louisville/Jefferson County', 'Louisville')
with open(file_name_upd, 'w') as f:
    f.write(data)
