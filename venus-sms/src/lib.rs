//! Based on official venus/multi-http-post's AFTER http_post / RexReport handler.
//! Application state contains only the two public mock delivery result fields.

use rialo_venus_proc_macro::rialo;

// Keep a remote timeout distinct from malformed delivery/account data.
const REX_TIMEOUT_ERROR: u32 = 5000;

#[derive(serde::Deserialize)]
#[serde(deny_unknown_fields)]
struct DeliveryResponse {
    message_id: String,
    status: String,
}

fn decode_delivery(data: &[u8]) -> Result<DeliveryResponse, rialo_s_program_error::ProgramError> {
    let response: DeliveryResponse = serde_json::from_slice(data)
        .map_err(|_| rialo_s_program_error::ProgramError::InvalidAccountData)?;
    if response.message_id.is_empty() || response.status != "delivered" {
        return Err(rialo_s_program_error::ProgramError::InvalidAccountData);
    }
    Ok(response)
}

fn decode_report(
    report: &rialo_rex_processor_interface::state::RexReport,
) -> Result<DeliveryResponse, rialo_s_program_error::ProgramError> {
    use rialo_s_program_error::ProgramError;
    use rialo_types::RexOutput;
    for output in report.outputs() {
        match output {
            RexOutput::Success(response) => {
                if let Some(data) = response.response.as_raw() {
                    return decode_delivery(data);
                }
            }
            RexOutput::RexError(rialo_types::RexError::Timeout { .. }) => {
                return Err(ProgramError::Custom(REX_TIMEOUT_ERROR));
            }
            RexOutput::RexError(_) | RexOutput::UnserializableResponse(_) => {
                return Err(ProgramError::InvalidAccountData);
            }
            _ => {}
        }
    }
    Err(ProgramError::InvalidAccountData)
}

rialo! {
    workflow {
        state {
            message_id: String,
            status: String,
        }
        program {
            use rialo_s_program::{entrypoint::ProgramResult, msg};
            use rialo_s_program_error::ProgramError;
            use rialo_rex_processor_interface::state::RexReport;

            initiating fn start(&mut self, relay_url: String, payload: String) -> ProgramResult {
                if !relay_url.starts_with("https://") {
                    return Err(ProgramError::InvalidArgument);
                }
                self.message_id = String::new();
                self.status = String::new();
                let body = payload.into_bytes();
                let content_type = "application/json".to_string();
                let headers = rialo_types::Headers::default();
                AFTER report = [http_post url: &relay_url body: &body content_type: &content_type headers: &headers request_delay_ms: 5000u64 validators_per_duty: 1u32]
                    CALL [receive_delivery report: report];
                Ok(())
            }

            handler fn receive_delivery(&mut self, report: RexReport) -> ProgramResult {
                let result = crate::decode_report(&report)?;
                self.message_id = result.message_id;
                self.status = result.status;
                msg!("SMS_STATE message_id={} status={}", self.message_id, self.status);
                Ok(())
            }

            control fn read_result(&mut self) -> ProgramResult {
                msg!("SMS_STATE message_id={} status={}", self.message_id, self.status);
                Ok(())
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::decode_delivery;

    #[test]
    fn reported_timeout_is_not_invalid_account_data() {
        use rialo_rex_processor_interface::state::{RexReport, RexUpdate};
        use rialo_s_program_error::ProgramError;
        // Borsh report bytes observed on DevNet: RexError::Timeout(300ms).
        // Also cover the newly configured 5000ms timeout.
        for duration in [300u64, 5000u64] {
            let mut data = vec![1, 10];
            data.extend_from_slice(&duration.to_le_bytes());
            let report = RexReport {
                rex_id: rialo_types::RexId::new(Default::default(), [0u8; 32]),
                round: Default::default(),
                updates: vec![RexUpdate::new(data, [0u8; 96])],
            };
            assert!(matches!(
                super::decode_report(&report),
                Err(ProgramError::Custom(super::REX_TIMEOUT_ERROR))
            ));
        }
    }

    #[test]
    fn preserves_delivery_fields() {
        let response = decode_delivery(br#"{"message_id":"mock_test","status":"delivered"}"#).unwrap();
        assert_eq!(response.message_id, "mock_test");
        assert_eq!(response.status, "delivered");
    }

    #[test]
    fn malformed_or_unsuccessful_response_is_not_success() {
        for data in [
            br#"{"status":"delivered"}"#.as_slice(),
            br#"{"message_id":"","status":"delivered"}"#.as_slice(),
            br#"{"message_id":"mock_test","status":"failed"}"#.as_slice(),
            br#"{"message_id":"mock_test","status":"delivered","extra":"value"}"#.as_slice(),
            b"not json".as_slice(),
        ] {
            assert!(decode_delivery(data).is_err());
        }
    }
}
