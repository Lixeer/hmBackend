package com.hospital.monitor.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.hospital.monitor.entity.BehaviorLog;
import com.hospital.monitor.entity.Patient;
import com.hospital.monitor.mapper.BehaviorLogMapper;
import com.hospital.monitor.mapper.PatientMapper;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;

@RestController
@RequestMapping("/api/stats")
@RequiredArgsConstructor
@Tag(name = "统计管理", description = "数据统计接口")
public class StatsController {

    private final PatientMapper patientMapper;
    private final BehaviorLogMapper behaviorLogMapper;

    @GetMapping
    @Operation(summary = "获取统计数据")
    public Object getStats() {
        long totalPatients = patientMapper.selectCount(null);

        QueryWrapper<Patient> abnormalWrapper = new QueryWrapper<>();
        abnormalWrapper.eq("status", "abnormal");
        long abnormalPatients = patientMapper.selectCount(abnormalWrapper);

        LocalDateTime startOfDay = LocalDateTime.of(LocalDate.now(), LocalTime.MIN);
        LocalDateTime endOfDay = LocalDateTime.of(LocalDate.now(), LocalTime.MAX);
        QueryWrapper<BehaviorLog> todayAbnormalWrapper = new QueryWrapper<>();
        todayAbnormalWrapper.eq("is_abnormal", 1)
                .ge("record_time", startOfDay)
                .le("record_time", endOfDay);
        long todayAbnormalRecords = behaviorLogMapper.selectCount(todayAbnormalWrapper);

        return new StatsResult(totalPatients, abnormalPatients, todayAbnormalRecords);
    }

    public record StatsResult(long totalPatients, long abnormalPatients, long todayAbnormalRecords) {}
}
