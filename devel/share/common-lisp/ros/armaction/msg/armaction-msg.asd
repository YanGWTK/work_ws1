
(cl:in-package :asdf)

(defsystem "armaction-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils :actionlib_msgs-msg
               :std_msgs-msg
)
  :components ((:file "_package")
    (:file "ArmControlAction" :depends-on ("_package_ArmControlAction"))
    (:file "_package_ArmControlAction" :depends-on ("_package"))
    (:file "ArmControlActionFeedback" :depends-on ("_package_ArmControlActionFeedback"))
    (:file "_package_ArmControlActionFeedback" :depends-on ("_package"))
    (:file "ArmControlActionGoal" :depends-on ("_package_ArmControlActionGoal"))
    (:file "_package_ArmControlActionGoal" :depends-on ("_package"))
    (:file "ArmControlActionResult" :depends-on ("_package_ArmControlActionResult"))
    (:file "_package_ArmControlActionResult" :depends-on ("_package"))
    (:file "ArmControlFeedback" :depends-on ("_package_ArmControlFeedback"))
    (:file "_package_ArmControlFeedback" :depends-on ("_package"))
    (:file "ArmControlGoal" :depends-on ("_package_ArmControlGoal"))
    (:file "_package_ArmControlGoal" :depends-on ("_package"))
    (:file "ArmControlResult" :depends-on ("_package_ArmControlResult"))
    (:file "_package_ArmControlResult" :depends-on ("_package"))
  ))