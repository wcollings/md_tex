#!/bin/python3
import subprocess as sub
import sys, json, getopt, os

def read_and_strip(fname):
	with open(fname,'r') as f:
		lines=[x.rstrip() for x in f.readlines()]
	return lines

def print_help():
	print("-h: prints this dialog")
	print("-c: does something")
	print("-s: soft run. Compile to tex file, but not to PDF")
	print("-t: specify a different template file")
	print("-o: specify an output file. Defaults to the same as input file, with a '.tex' file extension")

def set_kvp(d,k,v):
	if not k in d:
		d[k]=v

def setup_opts():
	global opts
	set_kvp(opts,'template','template.tex')
	set_kvp(opts,'soft',False)
	set_kvp(opts,'outf','stdout')
	set_kvp(opts,'iterations',1)

opts=json.load(open("info.json"))
setup_opts()

if len(sys.argv) < 2:
	print_help()
	sys.exit()
optlist, args = getopt.getopt(sys.argv[1:],'hcso:t')
for o,a in optlist:
	if o=='-t':
		opts['template']=a
		continue
	if o=='-h':
		print_help()
		continue
	if o=='-s':
		opts['soft']=True
		continue
	if o=='-o':
		opts['outf']=a
		continue
		
template=read_and_strip(opts['template'])
raw_f=sys.argv[-1]
options=opts['default']
if raw_f in opts:
	options=opts[raw_f]

sp_cmd=["pandoc",'-f','markdown','-t','latex',raw_f, "-o", "temp.tex", "--wrap=preserve"]

out=sub.run(sp_cmd)
lines=read_and_strip("temp.tex")
os.remove("temp.tex")
lines_to_remove=[]
for i in range(len(lines)):
	line=lines[i]
	if '\\[' in line or '\\]' in line:
		lines[i]="$$"
	if 'tightlist' in line or 'labelenum' in line:
		lines_to_remove.append(i)
	
for i in lines_to_remove[::-1]:
	lines.pop(i)
	
for i in range(len(template)):
	line=template[i]
	if "\\title" in line:
		if "hw" in raw_f:
			doc_title="Homework "+raw_f[2:3]
		else:
			doc_title=raw_f[:raw_f.find('.')]
		line="\\title{{{}\\\\{}}}".format(options['class'],doc_title)
		template[i]=line
		continue
	if '\\date' in line:
		line="\\date{{{}}}".format(options['date'])
		template[i]=line
		continue
	if '%body' in line:
		template[i:i+1]=lines
		continue

if opts['outf']=='stdout':
	print(template)
else:
	with open(opts['outf'],'w') as out:
		for line in template:
			out.write(line+'\n')
	if opts['soft']==False:
		compile_cmd=['pdflatex',opts['outf']]
		print("compiling...")
		for i in range(opts['iterations']):
			sub.run(compile_cmd)
		if opts["keep_intermediate_files"]==False:
			extensions=[".log",".aux"]
			fname=opts['outf'][:opts['outf'].find('.')]
			print(fname)
