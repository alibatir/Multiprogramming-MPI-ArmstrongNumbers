# Ali BATIR
# 2015400261
# Compiling
# Working
from mpi4py import MPI
import random 
import sys

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

workers=size-1
#get array size (A)
ARRAYSIZE=int(sys.argv[1])
#find the size that divides the array
chunksize=ARRAYSIZE/workers

#master process
if rank == 0:
	#create an array of numbers from 1 to ARRAYSIZE
	array=[]
	for i in range(ARRAYSIZE):
		array.append(i+1)
	#move array elements into a different order
	random.shuffle(array)

	for i in range(workers):
		#divide the array and create subarrays 
		subarray=[]
		for j in range(chunksize):
			subarray.append(array[j])
		#send subarrays to worker processes 
		comm.send(subarray, dest=(i+1), tag=1)
		#remove first chunksize elements from array
		array=array[chunksize:len(array)]

	#create an array for keeping armstrong numbers
	Armstrong=[]		
	for i in range(workers):
		#receive the array of Armstrong numbers from each worker 
		get_armstrong_numbers=comm.recv(tag=2)
		#append all elements of get_armstrong_numbers to Armstrong array
		Armstrong.extend(get_armstrong_numbers)

	#receive sum of Armstrong numbers from last worker
	collective_sum_result=comm.recv(source=workers,tag=5)
	print('MASTER: Sum of all Armstrong numbers: '+str(collective_sum_result))

	#sort the array of armstrong numbers
	Armstrong.sort()
	#print armstrong numbers to armstrong.txt
	with open('armstrong.txt', 'w') as f:
		for number in Armstrong:
			f.write("%s\n" % number)
#worker process
else:
	#receive the partition of the array
	receive=comm.recv(source=0,tag=1)
	#Finding Armstrong Numbers from the array that is received
	Armstrong_numbers=[]
	sum_armstrong=0
	#control all numbers from 0 to chunksize
	#chunksize:the size of the array elements for each worker process
	for i in range(chunksize): 
		digit=0
		#take a number from subarray
		number=receive[i]
		#find out what how many digits are there in our number
		while number!=0:
			#get the number except the last digit
			number=number/10
			digit=digit+1 #increase the number of digit 
		count=digit
		#take the same number from the array again
		number=receive[i]
		multiply=1
		sum=0
		#calculate the sum of the Armstrong numbers
		while number!=0:
			#compute the remainder that results from performing integer division
			remainder=number%10
			#multiply every digit 'digit' times and sum them
			while count!=0:
				multiply=multiply*remainder
				count=count-1 #decrease the number of digit  
			sum = sum + multiply
			count=digit
			#get the number except the last digit
			number=number/10
			multiply=1
		#if the number is Armstrong number
		if sum==receive[i]:
			#add the armstrong number to array
			Armstrong_numbers.append(receive[i])
			sum_armstrong=sum_armstrong+receive[i]
	
	print("Sum of Armstrong numbers in Process " +  str(rank) + " = " + str(sum_armstrong))

	#send the found Armstrong numbers in its partition to Master process
	comm.send(Armstrong_numbers,dest=0,tag=2)

	receive_sum_armstrong=0
	if rank!=1:
		#receive the sum of the armstrong numbers from previous process
		receive_sum_armstrong=comm.recv(source=rank-1,tag=4)
		#add sum of armstrong numbers to collective sum
    	collective_sum=sum_armstrong+receive_sum_armstrong
    	#print("Collective sum of Armstrong numbers in Process " +  str(rank) + " = " + str(collective_sum))
	#if rank is not equal to rank of the last worker
	if rank!=workers:
		#each process should send their sum to the next process
		comm.send(collective_sum,dest=rank+1,tag=4)
	else:
		#The last worker sends the final sum to master
		comm.send(collective_sum,dest=0,tag=5)