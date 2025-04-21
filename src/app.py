import re
from io import BytesIO
from xhtml2pdf import pisa
import markdown2
import streamlit as st
from src.crew.crew import market_research_crew #
from loguru import logger
from crewai.crews.crew_output import CrewOutput

st.set_page_config(page_title='Research Agent', layout='wide')
st.title('Market Research & Use Case Generation Agent')

# --- Helper Functions ---
def remove_markdown_fences(text):
    """Removes the ```markdown ... ``` fences."""
    # Ensure input is a string
    text = str(text).strip()
    # Remove backtick markdown tags
    text = re.sub(r'^```markdown\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*```$', '', text)
    return text

def convert_markdown_to_pdf(markdown_content: str) -> BytesIO | None:
    """Converts a Markdown string to a PDF byte stream"""
    # Convert markdown to HTML
    try:
        html_content = markdown2.markdown(
            markdown_content,
            extras=["tables", "fenced-code-blocks", "strike", "break-on-newline"]
        )
        html_with_style = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8">
            <style>
            body {{ font-family: sans-serif; line-height: 1.6; }} h1, h2, h3 {{ color: #333; }}
            a {{ color: #007bff; text-decoration: none; }} ul {{ margin-left: 20px; }}
            li {{ margin-bottom: 5px; }} pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
            code {{ font-family: monospace; }} table {{ border-collapse: collapse; width: 100%; margin-bottom: 1em; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }} th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
        {html_content}
        </body>
        </html>
        """
    except Exception as e:
        logger.debug(f" Error converting Markdown to HTML: {str(e)}") # logger.debug error
        st.error(f"Error converting Markdown to HTML: {str(e)}")
        return None
    # Create PDF from HTML
    pdf_stream = BytesIO()
    try:
        pisa_status = pisa.CreatePDF(BytesIO(html_with_style.encode('utf-8')), dest=pdf_stream, encoding='utf-8')
        if pisa_status.err:
            logger.debug(f" Error during PDF generation: {pisa_status.err}") # logger.debug error
            st.error(f"Error during PDF generation: {pisa_status.err}")
            return None
        else:
            pdf_stream.seek(0)
            logger.debug(" PDF generation successful.") # logger.debug success
            return pdf_stream
    except Exception as e:
        logger.debug(f" Error converting HTML to PDF: {str(e)}") # logger.debug error
        st.error(f"Error converting HTML to PDF: {str(e)}")
        return None

# --- Main App Logic ---

st.markdown("---")
st.subheader("Enter the company or industry name you want to research")
col1, col2 = st.columns(2)

company_input = col1.text_input(label='Enter company name', key='company_name_input')
industry_input = col2.text_input(label='Enter industry name', key='industry_name_input')

run_button = st.button("✨ Generate Report", type="primary", disabled=not (company_input or industry_input))

# --- Initialize Session State ---
if 'crew_result' not in st.session_state:
    st.session_state.crew_result = None   
if 'run_triggered' not in st.session_state:
    st.session_state.run_triggered = False
if 'is_error' not in st.session_state:
    st.session_state.is_error = False

if run_button: 
    if not (company_input or industry_input): 
        st.error("Please provide either a Company Name or an Industry Name.")
    else:
        # Reset state for new run
        st.session_state.run_triggered = True
        st.session_state.is_error = False
        st.session_state.crew_result = None

        crew_inputs = {'company_name': company_input, 'industry_name': industry_input}
        target_display = company_input if company_input else industry_input
        logger.info(f"Run triggered for: {target_display}")
        
        try:
            with st.spinner(f"🤖 Crew is working on the report for **{target_display}**... This may take a few minutes."):
                logger.info("Kicking off Crew...")
                result_raw = market_research_crew.kickoff(inputs=crew_inputs)
                logger.info(f"Crew kickoff finished. Raw result type: {type(result_raw)}")

                # Check if result is valid before cleaning 
                if result_raw and isinstance(result_raw, str) and result_raw.strip():
                    result_clean = remove_markdown_fences(text=result_raw)
                    logger.debug("Result cleaned")
                    st.session_state.crew_result = result_clean
                    st.session_state.is_error = False
                elif result_raw is None:
                    logger.debug("Crew returned empty output.")
                    st.session_state.crew_result = "Error: Process completed but returned no result."
                    st.session_state.is_error = True
                elif result_raw and isinstance(result_raw, CrewOutput):
                    # Convert the Crew ouput to str and try again 
                    logger.debug("Converting raw response from crew to <str>")
                    try:
                        result_str = str(result_raw)
                        result_clean = remove_markdown_fences(text=result_str)
                        logger.info(f"Resposne cleaned and converted to: type(result_str)")
                        st.session_state.crew_result = result_clean
                        st.session_state.is_error = False
                    except Exception as e:
                        logger.error(f"Crew respose output type: {type(result_raw)}, but failed to convert to <str>")
                        st.error(f"Unable to process response type: {type(result_raw)}")
                        st.session_state.crew_result = "Error: Response Invalid and could not be converted to a valid response."
                        st.session_state.is_error = True

        except ConnectionError as e:
            logger.error(f"Connection Error during Kickoff: {str(e)}")
            st.error(f"Connection Error: {str(e)}")
            st.session_state.is_error = True
            st.session_state.crew_result = f"Error: Connection Error - {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected Error occured: {str(e)}")
            st.error(f"Unexpected Error: {str(e)}")
            st.exception(e)
            st.session_state.is_error = True
            st.session_state.crew_result = f"Unexpected Error: {str(e)}"

        logger.debug(f"Run finished. is_error: '{st.session_state.is_error}', Result stored: '{st.session_state.crew_result[:100]}'")

# --- Display results ---
if st.session_state.get('run_triggered', False):
    logger.debug("Checking display condition...")
    report_content = st.session_state.get('crew_result')
    is_error_flag = st.session_state.get('is_error', False)

    if report_content:
        st.markdown("---")
        st.subheader("📊 Generated Report")
        logger.debug("Entering display block.")

        if is_error_flag:
            st.error(report_content)
            logger.info(f"Displaying Error message: {report_content}")
        else:
            try:
                logger.debug("Attempting to display the report markdown.")
                st.markdown(report_content)
                logger.debug("Markdown displayed.")

                # Display download buttons only if the markdown content was displayed 
                st.markdown("---")
                st.subheader("⬇️ Download Report")

                base_filename = re.sub(r'[^\w\-]+', '_', company_input or industry_input or "report")

                # 1. Markdown Download button
                try:
                    st.download_button(
                        label='Download as Markdown (.md)',
                        data=report_content.encode('utf-8'),
                        file_name=f"{base_filename}.md",
                        mime="text/markdown"
                    )
                    logger.debug("Added MD download button")
                except Exception as e:
                    st.error(f"Error showing MD download button: {str(e)}")
                    logger.error("Could not display MD download button")
                
                # 2. PDF download button 
                try:
                    # Convert to pdf 
                    logger.info("Initiating markdown to pdf conversion")
                    pdf_buffer = convert_markdown_to_pdf(markdown_content=report_content)
                    if pdf_buffer:
                        st.download_button(
                            label='Download as PDf (.pdf)',
                            data=pdf_buffer,  # Already BytesIO object
                            file_name=f"{base_filename}.pdf",
                            mime="application/pdf",
                        )
                        logger.debug("Added PDF download button")
                    else:
                        st.error("Could not generate PDF version.")
                        logger.error("PDF buffer was none, button not added.")
                except Exception as e:
                    st.error(f"An error occurred during PDF conversion: {str(e)}")
                    logger.error("PDF conversion failed")
            
            except Exception as e:
                logger.error(f"Error in markdown dislplay block: {str(e)}")
                st.session_state.is_error = True
                st.session_state.crew_result = f"Error displaying report: {str(e)}"

    elif not is_error_flag:
        # If run was triggered but result is still None/empty and not marked as error
        st.info("Processing the report...")
        print("[DEBUG] Run triggered, but result is None/empty and not an error.")

