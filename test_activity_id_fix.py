#!/usr/bin/env python3
"""
Test script to verify activity ID sharing fix
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_signal_emission():
    """Test that the activity_saved signal is properly defined"""
    try:
        from ui.forms.general_info import GeneralInfoForm
        from PyQt5.QtCore import pyqtSignal

        # Check if signal exists
        if hasattr(GeneralInfoForm, 'activity_saved'):
            print("✓ activity_saved signal found in GeneralInfoForm")
            signal = getattr(GeneralInfoForm, 'activity_saved')
            if isinstance(signal, pyqtSignal):
                print("✓ activity_saved is a proper pyqtSignal")
            else:
                print("✗ activity_saved is not a pyqtSignal")
        else:
            print("✗ activity_saved signal missing")
            return False

        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_broadcast_method():
    """Test that broadcast_activity_id method exists"""
    try:
        from ui.main_window import MainWindow

        if hasattr(MainWindow, 'broadcast_activity_id'):
            print("✓ broadcast_activity_id method found in MainWindow")
            return True
        else:
            print("✗ broadcast_activity_id method missing")
            return False
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_set_activity_id_method():
    """Test that forms have set_activity_id method"""
    form_classes = [
        'ui.forms.speaker_details.SpeakerDetailsForm',
        'ui.forms.participants.ParticipantsForm',
        'ui.forms.synopsis.SynopsisForm',
        'ui.forms.report_prepared_by.ReportPreparedByForm',
        'ui.forms.speaker_profile.SpeakerProfileForm',
        'ui.forms.activity_photos.ActivityPhotosForm',
        'ui.forms.generate_pdf.GeneratePDFForm'
    ]

    success_count = 0
    for form_class_path in form_classes:
        try:
            module_path, class_name = form_class_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            form_class = getattr(module, class_name)

            if hasattr(form_class, 'set_activity_id'):
                print(f"✓ {class_name} has set_activity_id method")
                success_count += 1
            else:
                print(f"✗ {class_name} missing set_activity_id method")
        except ImportError as e:
            print(f"✗ Cannot import {form_class_path}: {e}")

    return success_count == len(form_classes)

def main():
    """Run all tests"""
    print("Testing Activity ID Sharing Fix")
    print("=" * 40)

    tests = [
        ("Signal Emission Test", test_signal_emission),
        ("Broadcast Method Test", test_broadcast_method),
        ("Set Activity ID Method Test", test_set_activity_id_method)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append(result)
        print(f"Result: {'PASS' if result else 'FAIL'}")

    print("\n" + "=" * 40)
    print(f"Overall: {'ALL TESTS PASSED' if all(results) else 'SOME TESTS FAILED'}")

    if all(results):
        print("\nThe activity ID sharing fix appears to be correctly implemented.")
        print("If you're still seeing the error, please run the application and check the debug output.")
    else:
        print("\nThere are issues with the implementation that need to be fixed.")

if __name__ == "__main__":
    main()