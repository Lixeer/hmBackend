package com.hospital.monitor.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;

@Data
@TableName("patient")
public class Patient implements Serializable {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String name;

    private Integer age;

    private String gender;

    @TableField("room_number")
    private String roomNumber;

    private String status = "normal";

    private Integer severity = 0;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;
}
