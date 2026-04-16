"""
Spam Checker Tool for analyzing email content and calculating spam score.
Uses heuristic-based approach to estimate likelihood of email being marked as spam.
"""

import re
import logging
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SpamCheckResult:
    """Result of spam check analysis."""
    spam_score: float  # 0.0 to 1.0, higher means more likely spam
    is_likely_spam: bool
    factors: Dict[str, Any]
    recommendations: List[str]

class SpamCheckerTool:
    """Tool for checking spam score of email content."""

    def __init__(self):
        # Spam trigger words and phrases
        self.spam_words = {
            'high_risk': [
                'free', 'guarantee', 'winner', 'won', 'prize', 'cash', 'money',
                'profit', 'earn', 'income', 'rich', 'wealth', 'loan', 'debt',
                'credit', 'mortgage', 'insurance', 'pharmacy', 'meds', 'pills',
                'viagra', 'cialis', 'weight loss', 'diet', 'fat burner',
                'make money', 'work from home', 'business opportunity',
                'click here', 'limited time', 'act now', 'urgent', 'expires',
                'buy now', 'order now', 'discount', 'sale', 'offer', 'deal'
            ],
            'medium_risk': [
                'please', 'help', 'assistance', 'support', 'information',
                'details', 'response', 'reply', 'contact', 'call', 'phone',
                'email', 'message', 'inquiry', 'question', 'concern'
            ]
        }

        # Suspicious patterns
        self.suspicious_patterns = [
            r'!!+',  # Multiple exclamation marks
            r'\$\s*\d+',  # Dollar amounts
            r'%\s*off',  # Percentage discounts
            r'[\d,]+\s*\+',  # Numbers with plus sign
            r'[A-Z]{5,}',  # Long sequences of uppercase letters
            r'https?://[^\s]+',  # URLs
            r'www\.[^\s]+',  # WWW domains
        ]

        # Trust indicators (reduce spam score)
        self.trust_indicators = [
            'unsubscribe', 'privacy policy', 'terms of service',
            'company', 'address', 'phone', 'contact',
            'best regards', 'sincerely', 'thank you',
            'regards', 'thanks', 'appreciate'
        ]

    def check_spam_score(
        self,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> SpamCheckResult:
        """
        Analyze email content for spam characteristics.

        Args:
            subject: Email subject line
            body: Email body (plain text)
            html_body: Optional HTML body

        Returns:
            SpamCheckResult object
        """
        logger.info("Checking spam score for email content")

        # Combine subject and body for analysis
        full_text = f"{subject} {body}"
        if html_body:
            # Strip HTML tags for text analysis
            import re
            html_text = re.sub('<[^<]+?>', ' ', html_body)
            full_text += f" {html_text}"

        # Convert to lowercase for analysis
        text_lower = full_text.lower()

        # Calculate spam score components
        word_score = self._calculate_word_score(text_lower)
        pattern_score = self._calculate_pattern_score(full_text)
        caps_score = self._calculate_caps_score(full_text)
        punctuation_score = self._calculate_punctuation_score(full_text)
        trust_score = self._calculate_trust_score(text_lower)

        # Combine scores (weighted average)
        spam_score = (
            word_score * 0.4 +
            pattern_score * 0.2 +
            caps_score * 0.15 +
            punctuation_score * 0.15 +
            trust_score * 0.1  # Trust score is inverted (lower is better)
        )

        # Normalize to 0-1 range
        spam_score = max(0.0, min(1.0, spam_score))

        # Determine if likely spam
        is_likely_spam = spam_score > 0.6

        # Identify contributing factors
        factors = {
            'word_score': round(word_score, 3),
            'pattern_score': round(pattern_score, 3),
            'caps_score': round(caps_score, 3),
            'punctuation_score': round(punctuation_score, 3),
            'trust_score': round(trust_score, 3),
            'spam_words_found': self._find_spam_words(text_lower),
            'suspicious_patterns_found': self._find_suspicious_patterns(full_text)
        }

        # Generate recommendations
        recommendations = self._generate_recommendations(factors, spam_score)

        result = SpamCheckResult(
            spam_score=round(spam_score, 3),
            is_likely_spam=is_likely_spam,
            factors=factors,
            recommendations=recommendations
        )

        logger.info(f"Spam check complete. Score: {spam_score:.3f}, Likely spam: {is_likely_spam}")
        return result

    def _calculate_word_score(self, text: str) -> float:
        """Calculate score based on spam trigger words."""
        high_risk_count = sum(1 for word in self.spam_words['high_risk'] if word in text)
        medium_risk_count = sum(1 for word in self.spam_words['medium_risk'] if word in text)

        # Normalize by text length (approximate word count)
        word_count = max(len(text.split()), 1)
        high_score = min(high_risk_count / (word_count * 0.1), 1.0)  # Cap at 1.0
        medium_score = min(medium_risk_count / (word_count * 0.2), 0.5)  # Cap at 0.5

        return min(high_score + medium_score, 1.0)

    def _calculate_pattern_score(self, text: str) -> float:
        """Calculate score based on suspicious patterns."""
        pattern_matches = 0
        for pattern in self.suspicious_patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            pattern_matches += matches

        # Normalize by text length
        text_length = max(len(text), 1)
        return min(pattern_matches / (text_length * 0.01), 1.0)

    def _calculate_caps_score(self, text: str) -> float:
        """Calculate score based on excessive capitalization."""
        if not text:
            return 0.0

        # Count uppercase letters
        uppercase_count = sum(1 for c in text if c.isalpha() and c.isupper())
        total_letters = sum(1 for c in text if c.isalpha())

        if total_letters == 0:
            return 0.0

        caps_ratio = uppercase_count / total_letters
        # Score increases significantly when > 30% uppercase
        if caps_ratio > 0.3:
            return min((caps_ratio - 0.3) * 2, 1.0)
        return 0.0

    def _calculate_punctuation_score(self, text: str) -> float:
        """Calculate score based on excessive punctuation."""
        if not text:
            return 0.0

        # Count exclamation and question marks
        exc_count = text.count('!')
        ques_count = text.count('?')
        total_punct = exc_count + ques_count

        # Normalize by sentence count (approximate)
        sentence_count = max(text.count('.') + text.count('!') + text.count('?'), 1)
        punct_per_sentence = total_punct / sentence_count

        # Score increases when > 2 punctuation marks per sentence
        if punct_per_sentence > 2:
            return min((punct_per_sentence - 2) * 0.3, 1.0)
        return 0.0

    def _calculate_trust_score(self, text: str) -> float:
        """Calculate trust indicator score (inverted - higher trust = lower spam score)."""
        trust_count = sum(1 for indicator in self.trust_indicators if indicator in text)
        # More trust indicators = lower spam score
        # Normalize and invert
        normalized_trust = min(trust_count / 3.0, 1.0)  # Cap at 3 indicators
        return 1.0 - normalized_trust  # Invert so higher trust = lower score

    def _find_spam_words(self, text: str) -> List[str]:
        """Find spam words present in text."""
        found_words = []
        all_spam_words = self.spam_words['high_risk'] + self.spam_words['medium_risk']
        for word in all_spam_words:
            if word in text:
                found_words.append(word)
        return found_words[:10]  # Limit to top 10

    def _find_suspicious_patterns(self, text: str) -> List[str]:
        """Find suspicious patterns in text."""
        found_patterns = []
        for pattern in self.suspicious_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                found_patterns.extend(matches[:3])  # Limit matches per pattern
        return found_patterns[:10]  # Limit total

    def _generate_recommendations(self, factors: Dict[str, Any], spam_score: float) -> List[str]:
        """Generate recommendations to reduce spam score."""
        recommendations = []

        if factors['word_score'] > 0.3:
            recommendations.append("Reduce spam trigger words like 'free', 'guarantee', 'winner', etc.")

        if factors['pattern_score'] > 0.3:
            recommendations.append("Limit use of dollar amounts, percentages, and excessive URLs.")

        if factors['caps_score'] > 0.3:
            recommendations.append("Reduce excessive use of capital letters.")

        if factors['punctuation_score'] > 0.3:
            recommendations.append("Limit exclamation marks and question marks.")

        if factors['trust_score'] > 0.5:  # Low trust indicators
            recommendations.append("Add trust indicators like unsubscribe link, company address, or professional closing.")

        if spam_score > 0.7:
            recommendations.append("Consider completely rewriting the email with more natural, professional language.")

        if not recommendations:
            recommendations.append("Email looks good! Spam score is low.")

        return recommendations


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    checker = SpamCheckerTool()

    # Test with spammy content
    subject1 = "FREE MONEY!!! GUARANTEED WINNER!!!"
    body1 = "You have WON $1,000,000!!! Click here NOW!!! Limited time offer!!! ACT FAST!!!"
    result1 = checker.check_spam_score(subject1, body1)
    print("Spammy Email:")
    print(f"Spam Score: {result1.spam_score}")
    print(f"Likely Spam: {result1.is_likely_spam}")
    print(f"Recommendations: {result1.recommendations}")

    print("\n" + "="*50 + "\n")

    # Test with legitimate content
    subject2 = "Following up on our conversation about Acme Corp"
    body2 = """Hi John,

It was great speaking with you last week about Acme Corp's expansion plans.
I wanted to follow up and see if you had any questions about the proposal I sent over.

Our solution has helped companies like yours reduce operational costs by 25% while improving team productivity.

Would you have 15 minutes for a quick call this week to discuss next steps?

Best regards,
Sarah Johnson
Business Development Manager
TechSolutions Inc.
sarah@techsolutions.com
(555) 123-4567
Unsubscribe: https://techsolutions.com/unsubscribe"""

    result2 = checker.check_spam_score(subject2, body2)
    print("Legitimate Email:")
    print(f"Spam Score: {result2.spam_score}")
    print(f"Likely Spam: {result2.is_likely_spam}")
    print(f"Recommendations: {result2.recommendations}")