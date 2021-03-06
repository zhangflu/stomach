#!/usr/bin/python

import torch
import torchvision
from torchvision.datasets import ImageFolder
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import numpy as np

def image_data_set(args, image_path):
	transform = transforms.Compose(
		[transforms.Scale(args.image_size), # transforms.Scale((256,256))
		transforms.RandomCrop(args.image_size), 
		transforms.ToTensor(),
	 	transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
	return ImageFolder(root=image_path, transform=transform)

def split_data_set(category_elems, splits):
	# indexes
	splitted_indexes = None
	for category in category_elems:
		elems = category_elems[category]
		elems = [elems[i] for i in torch.randperm(len(elems))]
		split = splits[category]
		if splitted_indexes is None:
			splitted_indexes = []
			for i in range(len(split)):
				splitted_indexes.append([])
		count = 0
		for i in range(len(split)):
			splitted_indexes[i] += elems[count : count + split[i]]
			count += split[i]
	# samplers 
	from torch.utils.data.sampler import SubsetRandomSampler
	return [SubsetRandomSampler(index) for index in splitted_indexes]

def get_splits_uniform(category_elems, splits_p):
	min_count = None
	lens = [len(category_elems[c]) for c in category_elems]
	min_count = min(lens)
	split = [int(min_count * p) for p in splits_p]
	split[-1] += min_count - sum(split)
	print '  data_len:', lens, 'split:', split
	return {c:split for c in category_elems}

def get_category_info(data_set):
	from misc import progress_bar
	category_elems = {}
	for i in range(len(data_set)):
		image, category = data_set[i]
		if not category_elems.has_key(category):
			category_elems[category] = []
		category_elems[category].append(i)
		progress_bar(i, len(data_set))
	return category_elems

def get_data_loaders(args, image_path, splits_p, transforms):
	print('Loading data ...')
	kwargs = {'num_workers': 1, 'pin_memory': True} if args.cuda else {}
	data_set = image_data_set(args, image_path)
	category_elems = get_category_info(data_set)
	splits = get_splits_uniform(category_elems, splits_p)
	samplers = split_data_set(category_elems, splits)
	return [DataLoader(data_set, batch_size=args.batch_size, sampler=s, **kwargs) for s in samplers]

if __name__ == '__main__':
	from cifar_main import parse_argument
	args = parse_argument(additional_arguments={'image-size':256, 'num_classes':4})
	image_path='Data/Normal'
	splits_p=[0.8, 0.1, 0.1]
	train_transform = transforms.Compose([
		transforms.Pad(args.image_size // 8),
		transforms.RandomCrop(args.image_size),
		transforms.RandomHorizontalFlip(),
	])
	trans = [train_transform, None, None]
	train_loader, eval_loader, test_loader = get_data_loaders(args, image_path, splits_p, trans)

	def inspect_data(loader):
		images, labels = iter(loader).next()
		print labels.view(1,-1)
		print('images.size()', images.size())
		img = torchvision.utils.make_grid(images)
		npimg = img.numpy()
		plt.imshow(np.transpose(npimg, (1, 2, 0)))
		plt.show()

	inspect_data(train_loader)
	inspect_data(eval_loader)
	inspect_data(test_loader)

