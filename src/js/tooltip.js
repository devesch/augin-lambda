import {
    ProjectData
} from './classes/ProjectData.js';

function tooltip() {
    var tooltip = document.querySelector('.tooltip');

    if (!tooltip) {
        return;
    }

    tooltip.addEventListener('mouseover', function () {
        var tooltipText = this.querySelector('.tooltip-text');
        tooltipText.style.visibility = 'visible';
        tooltipText.style.opacity = 1;
    });

    tooltip.addEventListener('mouseout', function () {
        var tooltipText = this.querySelector('.tooltip-text');
        tooltipText.style.visibility = 'hidden';
        tooltipText.style.opacity = 0;
    });
}

let isWebviewPage = location.href.includes(ProjectData.props["domainNameUrlVal"] + "/webview/");

if (isWebviewPage) {
    tooltip();
}