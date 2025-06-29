from slither import Slither
from slither.detectors import all_detectors
import inspect
from slither.detectors.abstract_detector import AbstractDetector

class SlitherScanner:
    def __init__(self):
        self.analyzed_paths = []

        self.affected_lines_mapping = dict()

        self.severity_score_mapping = {
            "Low"           : 1,
            "Medium"        : 5,
            "High"          : 8,
            "Critical"      : 10,
            "Informational" : 0,
            "Optimization"  : 0
        }

        self.severity_type_frequency = {
            "Low"           : 0,
            "Medium"        : 0,
            "High"          : 0,
            "Critical"      : 0,
            "Informational" : 0,
            "Optimization"  : 0
        }
    
    def solidity_analysis(self, path):
        try:
            slither = Slither(str(path))
            
            # Get all detector classes
            detectors_ = [getattr(all_detectors, name) for name in dir(all_detectors)]
            detector_classes = [d for d in detectors_ if inspect.isclass(d) and issubclass(d, AbstractDetector)]

            # Register all detectors
            for detector_cls in detector_classes:
                slither.register_detector(detector_cls)

            # Run detectors
            detector_resultss = slither.run_detectors()

            # Flatten the list of results (essentially merges the lists for the found vulnerabilities from each detector)
            detector_results = [item for sublist in detector_resultss for item in sublist]

            vulnerabilities_found = False

            affected_lines = []

            for result in detector_results:
                vulnerabilities_found = True

                # Get the specifications of each vulnerability

                #detector_name = result.get('check', 'N/A')
                #confidence = result.get('confidence', 'N/A')
                severity = result.get('impact', 'N/A')
                description = result.get('description', 'N/A')
                elements = result.get('elements', 'N/A')

                source_mapping = elements[0].get("source_mapping", {})
                lines = source_mapping.get("lines", [])

                print("-" * 20)

                affected_lines.append((lines[0], lines[-1]))
                print(f"Error: {lines[0]} - {lines[-1]}")

                print(description)
                print(f"Severity: {severity}")
                self.severity_type_frequency[severity] += 1

                print("-" * 20)

            self.affected_lines_mapping.update({path : affected_lines})

            if not vulnerabilities_found:
                print(f"No vulnerabilities found!")

        except FileNotFoundError:
            print(f"Error: Solidity file not found.")
        except Exception as e:
            print(f"An error occurred during analysis: {e}")

    """
        Generates a severity report based on the severity score mapping and frequency of each severity type.
    
        Each severity category has a corresponding score. The project's score is calculated by multiplying the
    frequency of each severity type by its score and summing them up.
        
        The overall score will be illustrated by a maximum of 5 stars, each lit up star meaning a higher degree of severity:

        0 stars - No vulnerability found
        1 stars - <= 10 vulnerabilities found, no high or critical vulnerabilities;
        2 stars - <= 25 vulnerabilities found  or  <= 2 high severity vulnerabilities , no critical vulnerabilities;
        3 stars -  > 25 vulnerabilities found  or  <= 5 high severity vulnerabilities , no critical vulnerabilities; (low risk of attacks, needs fix))
        4 stars - <= 10 high severity vulnerabilities, <= 2 critical vulnerabilities;  (high risk of attacks, needs immediate fix)
        5 stars -  > 10 high severity vulnerabilities or > 2 critical vulnerabilities; (critical risk of attacks, needs immediate fix)

        Baseline: High and critical severity vulnerabilities are the most important ones to address,
        as they can lead to significant security risks. Low and medium severity vulnerabilities "award" the project
        with at most 3 stars.
    """
    def generate_severity_report(self):
        self.stars = 0
        score = 0

        for severity, frequency in self.severity_type_frequency.items():
            if frequency > 0:
                score += frequency * self.severity_score_mapping[severity]

        critical_vulnerabilities = self.severity_type_frequency["Critical"]
        high_vulnerabilities     = self.severity_type_frequency["High"]
        medium_vulnerabilities   = self.severity_type_frequency["Medium"]
        low_vulnerabilities      = self.severity_type_frequency["Low"]
        vulnerabilities          = critical_vulnerabilities + high_vulnerabilities + medium_vulnerabilities + low_vulnerabilities

        if critical_vulnerabilities > 2 or high_vulnerabilities > 10:
            self.stars = 5
        elif critical_vulnerabilities <= 2 and critical_vulnerabilities > 0 or high_vulnerabilities > 5 and high_vulnerabilities <= 10:
            self.stars = 4
        elif high_vulnerabilities <= 5 and high_vulnerabilities > 2 and vulnerabilities > 25:
            self.stars = 3
        elif high_vulnerabilities <= 2 and high_vulnerabilities > 0 or vulnerabilities <= 25 and vulnerabilities > 10:
            self.stars = 2
        elif vulnerabilities <= 10 and vulnerabilities > 0 and high_vulnerabilities == 0 and critical_vulnerabilities == 0:
            self.stars = 1
            
        report_string  = "Security report:\n"
        report_string += f"Severity rating: {self.stars} / 5\n"
        report_string += f"Severity Score: {score}\n"

        report_result=""
        if self.stars == 1:
            report_result = "Result: Great"
        if self.stars == 2:
            report_result = "Result: Good"
        if self.stars == 3:
            report_result = "Result: Medium"
        if self.stars == 4:
            report_result = "Result: Vulnerable"
        if self.stars == 5:
            report_result = "Result: Critical"

        report_string += report_result + "\n"

        report_string += f"Severity frequency: {self.severity_type_frequency}\n"

        print(f"Severity rating: {self.stars} stars")
        print(f"Severity Score: {score}")
        print(f"Severity frequency: {self.severity_type_frequency}")

        with open("security_report.txt", "w") as report_file:
            report_file.write(report_string)

        return report_string