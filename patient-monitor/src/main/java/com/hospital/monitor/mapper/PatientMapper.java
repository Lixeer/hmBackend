package com.hospital.monitor.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.hospital.monitor.entity.Patient;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface PatientMapper extends BaseMapper<Patient> {
}
