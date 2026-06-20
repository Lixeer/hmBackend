package com.hospital.monitor.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("behavior_log")
public class BehaviorLog {

    @TableId(type = IdType.AUTO)
    private Long id;

    @TableField("patient_id")
    private Long patientId;

    @TableField("behavior_type")
    private String behaviorType;

    private String description;

    @TableField("is_abnormal")
    private Integer isAbnormal;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime recordTime;
}
