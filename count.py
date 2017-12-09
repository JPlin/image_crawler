import os,sys

if __name__ == '__main__':
	des_dir = input("input the selected dir:")
	full_dir = os.path.join(os.getcwd(),des_dir)
	dirs = os.listdir(full_dir)
	
	dic = {}
	sum = 0
	for dir in dirs:
		dic[dir] = len(os.listdir(os.path.join(full_dir,dir,'Images')))
		sum += dic[dir]
	print(dic)
	print(sum)