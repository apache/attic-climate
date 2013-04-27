<?php
class WizardTask {
	
	public $currentStep = '';
	public $steps = array();
	
	public function __construct() {}
	
	public function save() {
		$_SESSION['wizardTask'] = serialize($this);
	}
	
	public function setStep($which) {
		$this->currentStep = $which;
	}
	
	public function firstStep() {
		$this->goToStep($this->steps[0][0]);
	}
	
	public function nextStep() {
		for($i=0;$i<count($this->steps);$i++) {
			if (strtolower($this->steps[$i][0]) == strtolower($this->currentStep)) {
				return (isset($this->steps[$i + 1]))
					? $this->goToStep($this->steps[$i+1][0])
					: false;
			}
		}
	}
	
	public function previousStep($current) {
		for($i=0;$i<count($this->steps);$i++) {
			if (strtolower($this->steps[$i]) == strtolower($this->currentStep)) {
				return (isset($this->steps[$i - 1]))
					? $this->goToStep($this->steps[$i - 1][0])
					: false;
			}
		}
	}	
	
	protected function goToStep($step) {
		$this->save();
		header("Location: " . SITE_ROOT . "/wizard/step/" . $step);
		exit();
	}
	
	public function showPreviousNextLinks() {
		for($i=1;$i<count($this->steps);$i++) {
			if (strtolower($this->steps[$i][0]) == strtolower($this->currentStep)) { 
				echo "<div class='box nav'>Back to <a href='".SITE_ROOT
					."/wizard/step/{$this->steps[$i-1][0]}'>{$this->steps[$i-1][1]}</a></div>";
			}
		}
	}
}