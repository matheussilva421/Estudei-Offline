
import pypdf
import re

class PDFParser:
    def extract_topics(self, file_path):
        """
        Extracts topics from a PDF file using basic heuristics.
        Returns a list of topic strings.
        """
        topics = []
        try:
            reader = pypdf.PdfReader(file_path)
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() + "\n"
            
            # Heuristic: Split by lines
            lines = full_text.split('\n')
            
            # Regex patterns for topics (e.g., "1. Topic", "1.1. Subtopic", "• Topic", "- Topic")
            # We want to catch numbered lists or bullet points
            pattern = re.compile(r'^\s*(\d+(\.\d+)*\.?|•|-)\s+(.+)')
            
            for line in lines:
                line = line.strip()
                if not line: continue
                
                # Check match
                match = pattern.match(line)
                if match:
                    # Clean the topic text
                    topic_text = line # Keep the numbering/bullet for context? Or remove?
                    # Let's keep it as is for now, as it preserves structure visuals
                    topics.append(topic_text)
                elif len(line) > 5 and len(line) < 100 and line[0].isupper():
                     # Fallback for simple titles if no numbering, but risky (headers, etc.)
                     # For now, let's stick to strict patterns to avoid garbage
                     pass
                     
            return topics
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return []
