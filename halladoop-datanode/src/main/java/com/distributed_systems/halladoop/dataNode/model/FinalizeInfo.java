package com.distributed_systems.halladoop.dataNode.model;

public class FinalizeInfo {

	private String block_id;
	private int[] node_id;
	
	public String getBlock_id() {
		return block_id;
	}
	public void setBlock_id(String block_id) {
		this.block_id = block_id;
	}
	public int[] getNode_id() {
		return node_id;
	}
	public void setNode_id(int[] node_id) {
		this.node_id = node_id;
	}
	
	
}
