#!/usr/bin/env python3
"""Recover only table blocks and explanation pages present in immutable source."""
import copy

from apply_canonical_bank_explanation_wiring_v1 import canonical_source_questions, reviewed_table_sources


def main():
    source = canonical_source_questions()['marrow__PHYSIO_CH27_Q009']
    original = copy.deepcopy(source)
    cfg = {'reconstruction': {'orphanTableIds': ['PHYSIO_CH27_Q009_T01']},
           'displayTables': [{'table_id': 'PHYSIO_CH27_Q009_T01', 'source_page': 492}]}
    assert reviewed_table_sources(source, cfg) == cfg['displayTables']
    for field, value in [('table_id', 'invented-table'), ('source_page', 485)]:
        invalid = copy.deepcopy(cfg)
        invalid['displayTables'][0][field] = value
        try:
            reviewed_table_sources(source, invalid)
        except SystemExit:
            pass
        else:
            raise AssertionError('Accepted an unsupported table identity/page')
    invalid = copy.deepcopy(cfg)
    invalid['reconstruction']['orphanTableIds'] = ['invented-table']
    try:
        reviewed_table_sources(source, invalid)
    except SystemExit:
        pass
    else:
        raise AssertionError('Accepted a table absent from source blocks')
    assert source == original
    print('MARROW_ORPHAN_TABLE_RECOVERY_OK source_block_and_page_pinned=true immutable=true')


if __name__ == '__main__':
    main()
