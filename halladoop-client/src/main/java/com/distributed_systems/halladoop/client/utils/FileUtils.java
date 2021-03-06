package com.distributed_systems.halladoop.client.utils;

import com.distributed_systems.halladoop.client.HalladoopClient;
import com.distributed_systems.halladoop.dataNode.model.WriteData;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.util.ArrayList;
import java.util.List;

/**
 * Created by devin on 12/8/15.
 */
public class FileUtils {
    public static List<WriteData> createBlocks(File file) throws IOException {
        List<WriteData> blocks = new ArrayList<>();

        try (FileInputStream inputStream = new FileInputStream(file)) {
            FileChannel channel = inputStream.getChannel();
            int filesize = (int) (file.length() < HalladoopClient.BLOCK_SIZE ? file.length() : HalladoopClient.BLOCK_SIZE);
            ByteBuffer buffer = ByteBuffer.allocate(filesize);

            byte[] blockData = new byte[filesize];
            int blockCount = 0;

            while (channel.read(buffer) > 0) {
                buffer.flip();

                for (int i = 0; i < buffer.limit(); i++)
                {
                    blockData[i] = buffer.get();
                }

                buffer.clear();

                String blockId = "/" + file.getName() + "-" + blockCount;
                WriteData dataBlock = new WriteData(blockData, blockId);
                blocks.add(dataBlock);

                blockCount++;
            }
        }

        return blocks;
    }
}
