"""
Centralized Agent Logger
All agents use this file to log their actions to experiment_data.json
"""

from src.utils.logger import log_experiment, ActionType


def log_auditor_action(filename: str, pylint_score: float, input_prompt: str, 
                       output_response: str, status: str = "SUCCESS"):
    """
    Log Auditor's code analysis action.
    
    Args:
        filename: File being analyzed
        pylint_score: Pylint score (0.0 to 10.0)
        input_prompt: Prompt sent to LLM
        output_response: LLM's analysis response
        status: SUCCESS or FAILURE
    """
    log_experiment(
        agent_name="Auditor",
        model_used="gemini-1.5-flash",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": input_prompt,
            "output_response": output_response,
            "filename": filename,
            "pylint_score": str(pylint_score)
        },
        status=status
    )


def log_fixer_action(filename: str, input_prompt: str, output_response: str,
                     changes_applied: bool, status: str = "SUCCESS"):
    """
    Log Fixer's code correction action.
    
    Args:
        filename: File being fixed
        input_prompt: Prompt with fix instructions
        output_response: Description of applied fixes
        changes_applied: Whether changes were saved
        status: SUCCESS or FAILURE
    """
    log_experiment(
        agent_name="Fixer",
        model_used="gemini-1.5-pro",
        action=ActionType.FIX,
        details={
            "input_prompt": input_prompt,
            "output_response": output_response,
            "filename": filename,
            "changes_applied": changes_applied
        },
        status=status
    )


def log_judge_action(filename: str, test_filename: str, test_output: str,
                     generation_message: str, model_used: str = "N/A",
                     status: str = "SUCCESS"):
    """
    Log Judge's test execution and analysis action.
    
    Args:
        filename: File being tested
        test_filename: Test file used
        test_output: Pytest output
        generation_message: Whether tests were generated or reused
        model_used: Model used if tests were generated
        status: SUCCESS or FAILURE
    """
    log_experiment(
        agent_name="Judge",
        model_used=model_used,
        action=ActionType.DEBUG,
        details={
            "input_prompt": f"Testing file: {filename}",
            "output_response": test_output,
            "test_filename": test_filename,
            "generation_message": generation_message
        },
        status=status
    )


def log_system_startup(target_directory: str):
    """Log system startup."""
    log_experiment(
        agent_name="System",
        model_used="N/A",
        action="STARTUP",
        details={
            "input_prompt": "System initialization",
            "output_response": f"Refactoring Swarm started on {target_directory}",
            "target_directory": target_directory
        },
        status="INFO"
    )


def log_system_completion(files_processed: int, successful: int, failed: int):
    """Log system completion with summary."""
    log_experiment(
        agent_name="System",
        model_used="N/A",
        action="COMPLETION",
        details={
            "input_prompt": "System shutdown",
            "output_response": f"Processed {files_processed} files: {successful} successful, {failed} failed",
            "files_processed": files_processed,
            "successful": successful,
            "failed": failed
        },
        status="INFO"
    )
