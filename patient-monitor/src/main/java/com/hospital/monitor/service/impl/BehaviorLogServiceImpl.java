package com.hospital.monitor.service.impl;

import com.hospital.monitor.entity.BehaviorLog;
import com.hospital.monitor.mapper.BehaviorLogMapper;
import com.hospital.monitor.service.BehaviorLogService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class BehaviorLogServiceImpl implements BehaviorLogService {

    private final BehaviorLogMapper behaviorLogMapper;

    @Override
    public void saveLog(BehaviorLog behaviorLog) {
        behaviorLogMapper.insert(behaviorLog);
    }
}
