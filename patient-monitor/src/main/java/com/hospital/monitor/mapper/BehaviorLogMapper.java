package com.hospital.monitor.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.hospital.monitor.entity.BehaviorLog;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface BehaviorLogMapper extends BaseMapper<BehaviorLog> {

    @Select("SELECT * FROM behavior_log WHERE patient_id = #{patientId} ORDER BY record_time DESC LIMIT 10")
    List<BehaviorLog> selectTop10ByPatientId(Long patientId);
}
