from __future__ import annotations

import math
from typing import Any, Callable, Mapping

from export_portfolio.intake.initiative import DomainRecord, RuleResult, bounded, finite_number, normalized_text

RuleFunction = Callable[[DomainRecord, Mapping[str, Any]], RuleResult]

def _number(record: DomainRecord, field: str) -> float:
    value = record.payload.get(field)
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return finite_number(value)
    text = normalized_text(value)
    if not text:
        return 0.0
    try:
        return finite_number(text)
    except ValueError:
        return float(sum(ord(ch) for ch in text) % 101)

def _context_number(context: Mapping[str, Any], key: str, default: float) -> float:
    try:
        return finite_number(context.get(key, default))
    except ValueError:
        return default

def _result(code: str, value: float, threshold: float, higher_is_better: bool, message: str, evidence: dict[str, Any]) -> RuleResult:
    distance = (value - threshold) if higher_is_better else (threshold - value)
    passed = distance >= 0
    scale = max(1.0, abs(threshold))
    score = bounded(0.5 + distance / (2.0 * scale))
    severity = 'info' if passed else ('critical' if score < 0.2 else 'error')
    return RuleResult(code, passed, score, severity, message, evidence)

def check_product_family_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'product_family')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_product_family_presence_threshold', 10.333)
    return _result('check_product_family_presence', adjusted, threshold, True, 'validates product_family presence',
                   {'field': 'product_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_product_family_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'product_family')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_product_family_range_threshold', 12.667)
    return _result('check_product_family_range', adjusted, threshold, True, 'validates product_family range',
                   {'field': 'product_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_product_family_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'product_family')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_product_family_stability_threshold', 15.0)
    return _result('check_product_family_stability', adjusted, threshold, False, 'validates product_family stability',
                   {'field': 'product_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_product_family_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'product_family')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_product_family_freshness_threshold', 17.333)
    return _result('check_product_family_freshness', adjusted, threshold, True, 'validates product_family freshness',
                   {'field': 'product_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_product_family_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'product_family')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_product_family_coverage_threshold', 19.667)
    return _result('check_product_family_coverage', adjusted, threshold, True, 'validates product_family coverage',
                   {'field': 'product_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_product_family_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'product_family')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_product_family_consistency_threshold', 22.0)
    return _result('check_product_family_consistency', adjusted, threshold, False, 'validates product_family consistency',
                   {'field': 'product_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_product_family_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'product_family')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_product_family_risk_threshold', 24.333)
    return _result('check_product_family_risk', adjusted, threshold, True, 'validates product_family risk',
                   {'field': 'product_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_product_family_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'product_family')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_product_family_confidence_threshold', 26.667)
    return _result('check_product_family_confidence', adjusted, threshold, True, 'validates product_family confidence',
                   {'field': 'product_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_product_family_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'product_family')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_product_family_dependency_threshold', 29.0)
    return _result('check_product_family_dependency', adjusted, threshold, False, 'validates product_family dependency',
                   {'field': 'product_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_product_family_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'product_family')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_product_family_readiness_threshold', 31.333)
    return _result('check_product_family_readiness', adjusted, threshold, True, 'validates product_family readiness',
                   {'field': 'product_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_country_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_country')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_target_country_presence_threshold', 9.333)
    return _result('check_target_country_presence', adjusted, threshold, True, 'validates target_country presence',
                   {'field': 'target_country', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_country_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_country')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_target_country_range_threshold', 11.667)
    return _result('check_target_country_range', adjusted, threshold, False, 'validates target_country range',
                   {'field': 'target_country', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_country_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_country')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_target_country_stability_threshold', 14.0)
    return _result('check_target_country_stability', adjusted, threshold, True, 'validates target_country stability',
                   {'field': 'target_country', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_country_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_country')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_target_country_freshness_threshold', 16.333)
    return _result('check_target_country_freshness', adjusted, threshold, True, 'validates target_country freshness',
                   {'field': 'target_country', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_country_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_country')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_target_country_coverage_threshold', 18.667)
    return _result('check_target_country_coverage', adjusted, threshold, False, 'validates target_country coverage',
                   {'field': 'target_country', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_country_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_country')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_target_country_consistency_threshold', 21.0)
    return _result('check_target_country_consistency', adjusted, threshold, True, 'validates target_country consistency',
                   {'field': 'target_country', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_country_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_country')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_target_country_risk_threshold', 23.333)
    return _result('check_target_country_risk', adjusted, threshold, True, 'validates target_country risk',
                   {'field': 'target_country', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_country_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_country')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_target_country_confidence_threshold', 25.667)
    return _result('check_target_country_confidence', adjusted, threshold, False, 'validates target_country confidence',
                   {'field': 'target_country', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_country_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_country')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_target_country_dependency_threshold', 28.0)
    return _result('check_target_country_dependency', adjusted, threshold, True, 'validates target_country dependency',
                   {'field': 'target_country', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_country_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_country')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_target_country_readiness_threshold', 30.333)
    return _result('check_target_country_readiness', adjusted, threshold, True, 'validates target_country readiness',
                   {'field': 'target_country', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_scenario_proof_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'scenario_proof')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_scenario_proof_presence_threshold', 8.333)
    return _result('check_scenario_proof_presence', adjusted, threshold, False, 'validates scenario_proof presence',
                   {'field': 'scenario_proof', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_scenario_proof_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'scenario_proof')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_scenario_proof_range_threshold', 10.667)
    return _result('check_scenario_proof_range', adjusted, threshold, True, 'validates scenario_proof range',
                   {'field': 'scenario_proof', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_scenario_proof_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'scenario_proof')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_scenario_proof_stability_threshold', 13.0)
    return _result('check_scenario_proof_stability', adjusted, threshold, True, 'validates scenario_proof stability',
                   {'field': 'scenario_proof', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_scenario_proof_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'scenario_proof')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_scenario_proof_freshness_threshold', 15.333)
    return _result('check_scenario_proof_freshness', adjusted, threshold, False, 'validates scenario_proof freshness',
                   {'field': 'scenario_proof', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_scenario_proof_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'scenario_proof')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_scenario_proof_coverage_threshold', 17.667)
    return _result('check_scenario_proof_coverage', adjusted, threshold, True, 'validates scenario_proof coverage',
                   {'field': 'scenario_proof', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_scenario_proof_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'scenario_proof')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_scenario_proof_consistency_threshold', 20.0)
    return _result('check_scenario_proof_consistency', adjusted, threshold, True, 'validates scenario_proof consistency',
                   {'field': 'scenario_proof', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_scenario_proof_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'scenario_proof')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_scenario_proof_risk_threshold', 22.333)
    return _result('check_scenario_proof_risk', adjusted, threshold, False, 'validates scenario_proof risk',
                   {'field': 'scenario_proof', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_scenario_proof_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'scenario_proof')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_scenario_proof_confidence_threshold', 24.667)
    return _result('check_scenario_proof_confidence', adjusted, threshold, True, 'validates scenario_proof confidence',
                   {'field': 'scenario_proof', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_scenario_proof_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'scenario_proof')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_scenario_proof_dependency_threshold', 27.0)
    return _result('check_scenario_proof_dependency', adjusted, threshold, True, 'validates scenario_proof dependency',
                   {'field': 'scenario_proof', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_scenario_proof_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'scenario_proof')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_scenario_proof_readiness_threshold', 29.333)
    return _result('check_scenario_proof_readiness', adjusted, threshold, False, 'validates scenario_proof readiness',
                   {'field': 'scenario_proof', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_standard_gap_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'standard_gap')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_standard_gap_presence_threshold', 31.667)
    return _result('check_standard_gap_presence', adjusted, threshold, True, 'validates standard_gap presence',
                   {'field': 'standard_gap', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_standard_gap_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'standard_gap')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_standard_gap_range_threshold', 9.667)
    return _result('check_standard_gap_range', adjusted, threshold, True, 'validates standard_gap range',
                   {'field': 'standard_gap', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_standard_gap_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'standard_gap')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_standard_gap_stability_threshold', 12.0)
    return _result('check_standard_gap_stability', adjusted, threshold, False, 'validates standard_gap stability',
                   {'field': 'standard_gap', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_standard_gap_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'standard_gap')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_standard_gap_freshness_threshold', 14.333)
    return _result('check_standard_gap_freshness', adjusted, threshold, True, 'validates standard_gap freshness',
                   {'field': 'standard_gap', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_standard_gap_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'standard_gap')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_standard_gap_coverage_threshold', 16.667)
    return _result('check_standard_gap_coverage', adjusted, threshold, True, 'validates standard_gap coverage',
                   {'field': 'standard_gap', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_standard_gap_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'standard_gap')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_standard_gap_consistency_threshold', 19.0)
    return _result('check_standard_gap_consistency', adjusted, threshold, False, 'validates standard_gap consistency',
                   {'field': 'standard_gap', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_standard_gap_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'standard_gap')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_standard_gap_risk_threshold', 21.333)
    return _result('check_standard_gap_risk', adjusted, threshold, True, 'validates standard_gap risk',
                   {'field': 'standard_gap', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_standard_gap_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'standard_gap')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_standard_gap_confidence_threshold', 23.667)
    return _result('check_standard_gap_confidence', adjusted, threshold, True, 'validates standard_gap confidence',
                   {'field': 'standard_gap', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_standard_gap_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'standard_gap')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_standard_gap_dependency_threshold', 26.0)
    return _result('check_standard_gap_dependency', adjusted, threshold, False, 'validates standard_gap dependency',
                   {'field': 'standard_gap', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_standard_gap_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'standard_gap')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_standard_gap_readiness_threshold', 28.333)
    return _result('check_standard_gap_readiness', adjusted, threshold, True, 'validates standard_gap readiness',
                   {'field': 'standard_gap', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_partner_strength_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'partner_strength')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_partner_strength_presence_threshold', 30.667)
    return _result('check_partner_strength_presence', adjusted, threshold, True, 'validates partner_strength presence',
                   {'field': 'partner_strength', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_partner_strength_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'partner_strength')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_partner_strength_range_threshold', 8.667)
    return _result('check_partner_strength_range', adjusted, threshold, False, 'validates partner_strength range',
                   {'field': 'partner_strength', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_partner_strength_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'partner_strength')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_partner_strength_stability_threshold', 11.0)
    return _result('check_partner_strength_stability', adjusted, threshold, True, 'validates partner_strength stability',
                   {'field': 'partner_strength', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_partner_strength_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'partner_strength')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_partner_strength_freshness_threshold', 13.333)
    return _result('check_partner_strength_freshness', adjusted, threshold, True, 'validates partner_strength freshness',
                   {'field': 'partner_strength', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_partner_strength_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'partner_strength')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_partner_strength_coverage_threshold', 15.667)
    return _result('check_partner_strength_coverage', adjusted, threshold, False, 'validates partner_strength coverage',
                   {'field': 'partner_strength', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_partner_strength_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'partner_strength')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_partner_strength_consistency_threshold', 18.0)
    return _result('check_partner_strength_consistency', adjusted, threshold, True, 'validates partner_strength consistency',
                   {'field': 'partner_strength', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_partner_strength_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'partner_strength')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_partner_strength_risk_threshold', 20.333)
    return _result('check_partner_strength_risk', adjusted, threshold, True, 'validates partner_strength risk',
                   {'field': 'partner_strength', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_partner_strength_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'partner_strength')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_partner_strength_confidence_threshold', 22.667)
    return _result('check_partner_strength_confidence', adjusted, threshold, False, 'validates partner_strength confidence',
                   {'field': 'partner_strength', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_partner_strength_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'partner_strength')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_partner_strength_dependency_threshold', 25.0)
    return _result('check_partner_strength_dependency', adjusted, threshold, True, 'validates partner_strength dependency',
                   {'field': 'partner_strength', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_partner_strength_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'partner_strength')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_partner_strength_readiness_threshold', 27.333)
    return _result('check_partner_strength_readiness', adjusted, threshold, True, 'validates partner_strength readiness',
                   {'field': 'partner_strength', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_localization_effort_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'localization_effort')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_localization_effort_presence_threshold', 29.667)
    return _result('check_localization_effort_presence', adjusted, threshold, False, 'validates localization_effort presence',
                   {'field': 'localization_effort', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_localization_effort_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'localization_effort')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_localization_effort_range_threshold', 32.0)
    return _result('check_localization_effort_range', adjusted, threshold, True, 'validates localization_effort range',
                   {'field': 'localization_effort', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_localization_effort_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'localization_effort')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_localization_effort_stability_threshold', 10.0)
    return _result('check_localization_effort_stability', adjusted, threshold, True, 'validates localization_effort stability',
                   {'field': 'localization_effort', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_localization_effort_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'localization_effort')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_localization_effort_freshness_threshold', 12.333)
    return _result('check_localization_effort_freshness', adjusted, threshold, False, 'validates localization_effort freshness',
                   {'field': 'localization_effort', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_localization_effort_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'localization_effort')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_localization_effort_coverage_threshold', 14.667)
    return _result('check_localization_effort_coverage', adjusted, threshold, True, 'validates localization_effort coverage',
                   {'field': 'localization_effort', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_localization_effort_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'localization_effort')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_localization_effort_consistency_threshold', 17.0)
    return _result('check_localization_effort_consistency', adjusted, threshold, True, 'validates localization_effort consistency',
                   {'field': 'localization_effort', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_localization_effort_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'localization_effort')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_localization_effort_risk_threshold', 19.333)
    return _result('check_localization_effort_risk', adjusted, threshold, False, 'validates localization_effort risk',
                   {'field': 'localization_effort', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_localization_effort_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'localization_effort')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_localization_effort_confidence_threshold', 21.667)
    return _result('check_localization_effort_confidence', adjusted, threshold, True, 'validates localization_effort confidence',
                   {'field': 'localization_effort', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_localization_effort_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'localization_effort')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_localization_effort_dependency_threshold', 24.0)
    return _result('check_localization_effort_dependency', adjusted, threshold, True, 'validates localization_effort dependency',
                   {'field': 'localization_effort', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_localization_effort_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'localization_effort')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_localization_effort_readiness_threshold', 26.333)
    return _result('check_localization_effort_readiness', adjusted, threshold, False, 'validates localization_effort readiness',
                   {'field': 'localization_effort', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_delivery_capacity_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'delivery_capacity')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_delivery_capacity_presence_threshold', 28.667)
    return _result('check_delivery_capacity_presence', adjusted, threshold, True, 'validates delivery_capacity presence',
                   {'field': 'delivery_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_delivery_capacity_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'delivery_capacity')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_delivery_capacity_range_threshold', 31.0)
    return _result('check_delivery_capacity_range', adjusted, threshold, True, 'validates delivery_capacity range',
                   {'field': 'delivery_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_delivery_capacity_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'delivery_capacity')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_delivery_capacity_stability_threshold', 9.0)
    return _result('check_delivery_capacity_stability', adjusted, threshold, False, 'validates delivery_capacity stability',
                   {'field': 'delivery_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_delivery_capacity_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'delivery_capacity')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_delivery_capacity_freshness_threshold', 11.333)
    return _result('check_delivery_capacity_freshness', adjusted, threshold, True, 'validates delivery_capacity freshness',
                   {'field': 'delivery_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_delivery_capacity_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'delivery_capacity')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_delivery_capacity_coverage_threshold', 13.667)
    return _result('check_delivery_capacity_coverage', adjusted, threshold, True, 'validates delivery_capacity coverage',
                   {'field': 'delivery_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_delivery_capacity_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'delivery_capacity')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_delivery_capacity_consistency_threshold', 16.0)
    return _result('check_delivery_capacity_consistency', adjusted, threshold, False, 'validates delivery_capacity consistency',
                   {'field': 'delivery_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_delivery_capacity_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'delivery_capacity')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_delivery_capacity_risk_threshold', 18.333)
    return _result('check_delivery_capacity_risk', adjusted, threshold, True, 'validates delivery_capacity risk',
                   {'field': 'delivery_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_delivery_capacity_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'delivery_capacity')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_delivery_capacity_confidence_threshold', 20.667)
    return _result('check_delivery_capacity_confidence', adjusted, threshold, True, 'validates delivery_capacity confidence',
                   {'field': 'delivery_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_delivery_capacity_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'delivery_capacity')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_delivery_capacity_dependency_threshold', 23.0)
    return _result('check_delivery_capacity_dependency', adjusted, threshold, False, 'validates delivery_capacity dependency',
                   {'field': 'delivery_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_delivery_capacity_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'delivery_capacity')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_delivery_capacity_readiness_threshold', 25.333)
    return _result('check_delivery_capacity_readiness', adjusted, threshold, True, 'validates delivery_capacity readiness',
                   {'field': 'delivery_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_expected_revenue_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'expected_revenue')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_expected_revenue_presence_threshold', 27.667)
    return _result('check_expected_revenue_presence', adjusted, threshold, True, 'validates expected_revenue presence',
                   {'field': 'expected_revenue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_expected_revenue_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'expected_revenue')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_expected_revenue_range_threshold', 30.0)
    return _result('check_expected_revenue_range', adjusted, threshold, False, 'validates expected_revenue range',
                   {'field': 'expected_revenue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_expected_revenue_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'expected_revenue')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_expected_revenue_stability_threshold', 8.0)
    return _result('check_expected_revenue_stability', adjusted, threshold, True, 'validates expected_revenue stability',
                   {'field': 'expected_revenue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_expected_revenue_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'expected_revenue')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_expected_revenue_freshness_threshold', 10.333)
    return _result('check_expected_revenue_freshness', adjusted, threshold, True, 'validates expected_revenue freshness',
                   {'field': 'expected_revenue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_expected_revenue_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'expected_revenue')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_expected_revenue_coverage_threshold', 12.667)
    return _result('check_expected_revenue_coverage', adjusted, threshold, False, 'validates expected_revenue coverage',
                   {'field': 'expected_revenue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_expected_revenue_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'expected_revenue')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_expected_revenue_consistency_threshold', 15.0)
    return _result('check_expected_revenue_consistency', adjusted, threshold, True, 'validates expected_revenue consistency',
                   {'field': 'expected_revenue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_expected_revenue_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'expected_revenue')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_expected_revenue_risk_threshold', 17.333)
    return _result('check_expected_revenue_risk', adjusted, threshold, True, 'validates expected_revenue risk',
                   {'field': 'expected_revenue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_expected_revenue_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'expected_revenue')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_expected_revenue_confidence_threshold', 19.667)
    return _result('check_expected_revenue_confidence', adjusted, threshold, False, 'validates expected_revenue confidence',
                   {'field': 'expected_revenue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_expected_revenue_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'expected_revenue')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_expected_revenue_dependency_threshold', 22.0)
    return _result('check_expected_revenue_dependency', adjusted, threshold, True, 'validates expected_revenue dependency',
                   {'field': 'expected_revenue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_expected_revenue_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'expected_revenue')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_expected_revenue_readiness_threshold', 24.333)
    return _result('check_expected_revenue_readiness', adjusted, threshold, True, 'validates expected_revenue readiness',
                   {'field': 'expected_revenue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_currency_risk_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'currency_risk')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_currency_risk_presence_threshold', 26.667)
    return _result('check_currency_risk_presence', adjusted, threshold, False, 'validates currency_risk presence',
                   {'field': 'currency_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_currency_risk_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'currency_risk')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_currency_risk_range_threshold', 29.0)
    return _result('check_currency_risk_range', adjusted, threshold, True, 'validates currency_risk range',
                   {'field': 'currency_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_currency_risk_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'currency_risk')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_currency_risk_stability_threshold', 31.333)
    return _result('check_currency_risk_stability', adjusted, threshold, True, 'validates currency_risk stability',
                   {'field': 'currency_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_currency_risk_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'currency_risk')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_currency_risk_freshness_threshold', 9.333)
    return _result('check_currency_risk_freshness', adjusted, threshold, False, 'validates currency_risk freshness',
                   {'field': 'currency_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_currency_risk_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'currency_risk')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_currency_risk_coverage_threshold', 11.667)
    return _result('check_currency_risk_coverage', adjusted, threshold, True, 'validates currency_risk coverage',
                   {'field': 'currency_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_currency_risk_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'currency_risk')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_currency_risk_consistency_threshold', 14.0)
    return _result('check_currency_risk_consistency', adjusted, threshold, True, 'validates currency_risk consistency',
                   {'field': 'currency_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_currency_risk_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'currency_risk')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_currency_risk_risk_threshold', 16.333)
    return _result('check_currency_risk_risk', adjusted, threshold, False, 'validates currency_risk risk',
                   {'field': 'currency_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_currency_risk_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'currency_risk')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_currency_risk_confidence_threshold', 18.667)
    return _result('check_currency_risk_confidence', adjusted, threshold, True, 'validates currency_risk confidence',
                   {'field': 'currency_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_currency_risk_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'currency_risk')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_currency_risk_dependency_threshold', 21.0)
    return _result('check_currency_risk_dependency', adjusted, threshold, True, 'validates currency_risk dependency',
                   {'field': 'currency_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_currency_risk_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'currency_risk')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_currency_risk_readiness_threshold', 23.333)
    return _result('check_currency_risk_readiness', adjusted, threshold, False, 'validates currency_risk readiness',
                   {'field': 'currency_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_policy_risk_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'policy_risk')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_policy_risk_presence_threshold', 25.667)
    return _result('check_policy_risk_presence', adjusted, threshold, True, 'validates policy_risk presence',
                   {'field': 'policy_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_policy_risk_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'policy_risk')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_policy_risk_range_threshold', 28.0)
    return _result('check_policy_risk_range', adjusted, threshold, True, 'validates policy_risk range',
                   {'field': 'policy_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_policy_risk_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'policy_risk')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_policy_risk_stability_threshold', 30.333)
    return _result('check_policy_risk_stability', adjusted, threshold, False, 'validates policy_risk stability',
                   {'field': 'policy_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_policy_risk_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'policy_risk')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_policy_risk_freshness_threshold', 8.333)
    return _result('check_policy_risk_freshness', adjusted, threshold, True, 'validates policy_risk freshness',
                   {'field': 'policy_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_policy_risk_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'policy_risk')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_policy_risk_coverage_threshold', 10.667)
    return _result('check_policy_risk_coverage', adjusted, threshold, True, 'validates policy_risk coverage',
                   {'field': 'policy_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_policy_risk_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'policy_risk')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_policy_risk_consistency_threshold', 13.0)
    return _result('check_policy_risk_consistency', adjusted, threshold, False, 'validates policy_risk consistency',
                   {'field': 'policy_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_policy_risk_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'policy_risk')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_policy_risk_risk_threshold', 15.333)
    return _result('check_policy_risk_risk', adjusted, threshold, True, 'validates policy_risk risk',
                   {'field': 'policy_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_policy_risk_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'policy_risk')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_policy_risk_confidence_threshold', 17.667)
    return _result('check_policy_risk_confidence', adjusted, threshold, True, 'validates policy_risk confidence',
                   {'field': 'policy_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_policy_risk_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'policy_risk')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_policy_risk_dependency_threshold', 20.0)
    return _result('check_policy_risk_dependency', adjusted, threshold, False, 'validates policy_risk dependency',
                   {'field': 'policy_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_policy_risk_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'policy_risk')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_policy_risk_readiness_threshold', 22.333)
    return _result('check_policy_risk_readiness', adjusted, threshold, True, 'validates policy_risk readiness',
                   {'field': 'policy_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_support_cost_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'support_cost')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_support_cost_presence_threshold', 24.667)
    return _result('check_support_cost_presence', adjusted, threshold, True, 'validates support_cost presence',
                   {'field': 'support_cost', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_support_cost_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'support_cost')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_support_cost_range_threshold', 27.0)
    return _result('check_support_cost_range', adjusted, threshold, False, 'validates support_cost range',
                   {'field': 'support_cost', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_support_cost_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'support_cost')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_support_cost_stability_threshold', 29.333)
    return _result('check_support_cost_stability', adjusted, threshold, True, 'validates support_cost stability',
                   {'field': 'support_cost', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_support_cost_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'support_cost')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_support_cost_freshness_threshold', 31.667)
    return _result('check_support_cost_freshness', adjusted, threshold, True, 'validates support_cost freshness',
                   {'field': 'support_cost', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_support_cost_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'support_cost')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_support_cost_coverage_threshold', 9.667)
    return _result('check_support_cost_coverage', adjusted, threshold, False, 'validates support_cost coverage',
                   {'field': 'support_cost', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_support_cost_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'support_cost')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_support_cost_consistency_threshold', 12.0)
    return _result('check_support_cost_consistency', adjusted, threshold, True, 'validates support_cost consistency',
                   {'field': 'support_cost', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_support_cost_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'support_cost')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_support_cost_risk_threshold', 14.333)
    return _result('check_support_cost_risk', adjusted, threshold, True, 'validates support_cost risk',
                   {'field': 'support_cost', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_support_cost_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'support_cost')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_support_cost_confidence_threshold', 16.667)
    return _result('check_support_cost_confidence', adjusted, threshold, False, 'validates support_cost confidence',
                   {'field': 'support_cost', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_support_cost_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'support_cost')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_support_cost_dependency_threshold', 19.0)
    return _result('check_support_cost_dependency', adjusted, threshold, True, 'validates support_cost dependency',
                   {'field': 'support_cost', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_support_cost_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'support_cost')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_support_cost_readiness_threshold', 21.333)
    return _result('check_support_cost_readiness', adjusted, threshold, True, 'validates support_cost readiness',
                   {'field': 'support_cost', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_dependency_count_presence_threshold', 23.667)
    return _result('check_dependency_count_presence', adjusted, threshold, False, 'validates dependency_count presence',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_dependency_count_range_threshold', 26.0)
    return _result('check_dependency_count_range', adjusted, threshold, True, 'validates dependency_count range',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_dependency_count_stability_threshold', 28.333)
    return _result('check_dependency_count_stability', adjusted, threshold, True, 'validates dependency_count stability',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_dependency_count_freshness_threshold', 30.667)
    return _result('check_dependency_count_freshness', adjusted, threshold, False, 'validates dependency_count freshness',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_dependency_count_coverage_threshold', 8.667)
    return _result('check_dependency_count_coverage', adjusted, threshold, True, 'validates dependency_count coverage',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_dependency_count_consistency_threshold', 11.0)
    return _result('check_dependency_count_consistency', adjusted, threshold, True, 'validates dependency_count consistency',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_dependency_count_risk_threshold', 13.333)
    return _result('check_dependency_count_risk', adjusted, threshold, False, 'validates dependency_count risk',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_dependency_count_confidence_threshold', 15.667)
    return _result('check_dependency_count_confidence', adjusted, threshold, True, 'validates dependency_count confidence',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_dependency_count_dependency_threshold', 18.0)
    return _result('check_dependency_count_dependency', adjusted, threshold, True, 'validates dependency_count dependency',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_dependency_count_readiness_threshold', 20.333)
    return _result('check_dependency_count_readiness', adjusted, threshold, False, 'validates dependency_count readiness',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

RULES: tuple[RuleFunction, ...] = (
    check_product_family_presence,
    check_product_family_range,
    check_product_family_stability,
    check_product_family_freshness,
    check_product_family_coverage,
    check_product_family_consistency,
    check_product_family_risk,
    check_product_family_confidence,
    check_product_family_dependency,
    check_product_family_readiness,
    check_target_country_presence,
    check_target_country_range,
    check_target_country_stability,
    check_target_country_freshness,
    check_target_country_coverage,
    check_target_country_consistency,
    check_target_country_risk,
    check_target_country_confidence,
    check_target_country_dependency,
    check_target_country_readiness,
    check_scenario_proof_presence,
    check_scenario_proof_range,
    check_scenario_proof_stability,
    check_scenario_proof_freshness,
    check_scenario_proof_coverage,
    check_scenario_proof_consistency,
    check_scenario_proof_risk,
    check_scenario_proof_confidence,
    check_scenario_proof_dependency,
    check_scenario_proof_readiness,
    check_standard_gap_presence,
    check_standard_gap_range,
    check_standard_gap_stability,
    check_standard_gap_freshness,
    check_standard_gap_coverage,
    check_standard_gap_consistency,
    check_standard_gap_risk,
    check_standard_gap_confidence,
    check_standard_gap_dependency,
    check_standard_gap_readiness,
    check_partner_strength_presence,
    check_partner_strength_range,
    check_partner_strength_stability,
    check_partner_strength_freshness,
    check_partner_strength_coverage,
    check_partner_strength_consistency,
    check_partner_strength_risk,
    check_partner_strength_confidence,
    check_partner_strength_dependency,
    check_partner_strength_readiness,
    check_localization_effort_presence,
    check_localization_effort_range,
    check_localization_effort_stability,
    check_localization_effort_freshness,
    check_localization_effort_coverage,
    check_localization_effort_consistency,
    check_localization_effort_risk,
    check_localization_effort_confidence,
    check_localization_effort_dependency,
    check_localization_effort_readiness,
    check_delivery_capacity_presence,
    check_delivery_capacity_range,
    check_delivery_capacity_stability,
    check_delivery_capacity_freshness,
    check_delivery_capacity_coverage,
    check_delivery_capacity_consistency,
    check_delivery_capacity_risk,
    check_delivery_capacity_confidence,
    check_delivery_capacity_dependency,
    check_delivery_capacity_readiness,
    check_expected_revenue_presence,
    check_expected_revenue_range,
    check_expected_revenue_stability,
    check_expected_revenue_freshness,
    check_expected_revenue_coverage,
    check_expected_revenue_consistency,
    check_expected_revenue_risk,
    check_expected_revenue_confidence,
    check_expected_revenue_dependency,
    check_expected_revenue_readiness,
    check_currency_risk_presence,
    check_currency_risk_range,
    check_currency_risk_stability,
    check_currency_risk_freshness,
    check_currency_risk_coverage,
    check_currency_risk_consistency,
    check_currency_risk_risk,
    check_currency_risk_confidence,
    check_currency_risk_dependency,
    check_currency_risk_readiness,
    check_policy_risk_presence,
    check_policy_risk_range,
    check_policy_risk_stability,
    check_policy_risk_freshness,
    check_policy_risk_coverage,
    check_policy_risk_consistency,
    check_policy_risk_risk,
    check_policy_risk_confidence,
    check_policy_risk_dependency,
    check_policy_risk_readiness,
    check_support_cost_presence,
    check_support_cost_range,
    check_support_cost_stability,
    check_support_cost_freshness,
    check_support_cost_coverage,
    check_support_cost_consistency,
    check_support_cost_risk,
    check_support_cost_confidence,
    check_support_cost_dependency,
    check_support_cost_readiness,
    check_dependency_count_presence,
    check_dependency_count_range,
    check_dependency_count_stability,
    check_dependency_count_freshness,
    check_dependency_count_coverage,
    check_dependency_count_consistency,
    check_dependency_count_risk,
    check_dependency_count_confidence,
    check_dependency_count_dependency,
    check_dependency_count_readiness,
)

RULE_INDEX = {rule.__name__: rule for rule in RULES}

def evaluate(record: DomainRecord, context: Mapping[str, Any] | None = None) -> tuple[RuleResult, ...]:
    context = context or {}
    return tuple(rule(record, context) for rule in RULES)

def summarize(results: tuple[RuleResult, ...]) -> dict[str, Any]:
    if not results:
        return {'score': 0.0, 'passed': 0, 'failed': 0, 'critical': 0}
    return {'score': sum(item.score for item in results) / len(results),
            'passed': sum(item.passed for item in results),
            'failed': sum(not item.passed for item in results),
            'critical': sum(item.severity == 'critical' for item in results)}
