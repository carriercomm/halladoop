package com.distributed_systems.halladoop.dataNode.model;

import java.io.Serializable;

public enum Operation implements Serializable{
	READ,
	WRITE,
	DELETE
}
